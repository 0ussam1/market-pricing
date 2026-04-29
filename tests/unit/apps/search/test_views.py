import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from apps.search.models import Search


@pytest.mark.django_db
class TestSearchViews:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = get_user_model().objects.create_user(
            username="search-view-user",
            email="search-view@example.com",
            password="StrongPassword123!",
        )
        self.other_user = get_user_model().objects.create_user(
            username="other-search-user",
            email="other-search@example.com",
            password="StrongPassword123!",
        )
        self.client = APIClient()

    def test_create_search_requires_authentication(self):
        response = self.client.post(
            reverse("search-list-create"),
            {"query": "iphone", "platforms": ["amazon", "ebay"]},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("apps.search.views.run_search_pipeline.delay")
    def test_create_search_for_authenticated_user(self, mock_delay):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("search-list-create"),
            {"query": "iphone", "platforms": ["amazon", "ebay"]},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Search.objects.filter(user=self.user, query="iphone").exists()
        assert response.data["status"] == Search.Status.PENDING
        mock_delay.assert_called_once()

    @patch("apps.search.views.run_search_pipeline.delay")
    def test_create_search_deduplication(self, mock_delay):
        # Create an existing pending search
        existing = Search.objects.create(
            user=self.user,
            query="iphone",
            platforms=["amazon", "ebay"],
            status=Search.Status.PENDING
        )
        
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("search-list-create"),
            {"query": "iphone", "platforms": ["amazon", "ebay"]},
            format="json",
        )

        # Should return 200 OK and same ID
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == existing.id
        # Should NOT trigger a new task
        mock_delay.assert_not_called()

    def test_list_searches_only_returns_current_user_results(self):
        own_search = Search.objects.create(
            user=self.user,
            query="iphone",
            platforms=["amazon"],
            status=Search.Status.PENDING,
        )
        Search.objects.create(
            user=self.other_user,
            query="samsung",
            platforms=["ebay"],
            status=Search.Status.COMPLETED,
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("search-list-create"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == own_search.id

    def test_search_status_polling(self):
        search = Search.objects.create(
            user=self.user,
            query="iphone",
            platforms=["amazon"],
            status=Search.Status.PROCESSING
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("search-status", args=[search.id]))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == search.id
        assert response.data["status"] == Search.Status.PROCESSING
        assert "created_at" in response.data

    def test_status_polling_blocks_other_user(self):
        search = Search.objects.create(
            user=self.other_user,
            query="private",
            platforms=["amazon"],
            status=Search.Status.PENDING,
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("search-status", args=[search.id]))

        assert response.status_code == status.HTTP_404_NOT_FOUND
