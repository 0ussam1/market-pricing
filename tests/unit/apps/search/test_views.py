import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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

    def test_create_search_for_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("search-list-create"),
            {"query": "iphone", "platforms": ["amazon", "ebay"]},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Search.objects.filter(user=self.user, query="iphone").exists()
        assert response.data["user"] == self.user.id
        assert response.data["status"] == Search.Status.PENDING

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

    def test_retrieve_search_blocks_other_user_access(self):
        search = Search.objects.create(
            user=self.other_user,
            query="private",
            platforms=["amazon"],
            status=Search.Status.PENDING,
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("search-detail", args=[search.id]))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filter_searches_by_status(self):
        Search.objects.create(
            user=self.user,
            query="pending search",
            platforms=["amazon"],
            status=Search.Status.PENDING,
        )
        completed_search = Search.objects.create(
            user=self.user,
            query="completed search",
            platforms=["ebay"],
            status=Search.Status.COMPLETED,
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse("search-list-create"),
            {"status": Search.Status.COMPLETED},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == completed_search.id
