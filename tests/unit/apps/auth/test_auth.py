import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from django.conf import settings

@pytest.mark.django_db
class TestAuthentication:
    @pytest.fixture(autouse=True)
    def setup_user_model(self):
        self.User = get_user_model()

    def test_register_valid_user(self, client):
        url = reverse('register')
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert self.User.objects.filter(username="testuser").exists()

    def test_register_password_mismatch(self, client):
        url = reverse('register')
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "confirm_password": "WrongPassword123!"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirm_password" in response.data

    def test_register_weak_password(self, client):
        url = reverse('register')
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",
            "confirm_password": "123"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_register_duplicate_username(self, client):
        self.User.objects.create_user(
            username="testuser",
            email="existing@example.com",
            password="StrongPassword123!",
        )

        url = reverse('register')
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_login_success(self, client):
        # Create user first
        self.User.objects.create_user(username="loginuser", password="TestPassword123!")
        
        url = reverse('login')
        data = {"username": "loginuser", "password": "TestPassword123!"}
        response = client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        cookie = response.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']]
        assert settings.SIMPLE_JWT['AUTH_COOKIE'] in response.cookies
        assert cookie["httponly"]
        assert response.data["message"] == "Login successful"

    def test_login_invalid_credentials(self, client):
        url = reverse('login')
        data = {"username": "wronguser", "password": "wrongpassword"}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_clears_cookie(self, client):
        url = reverse('logout')
        response = client.post(url)
        assert response.status_code == status.HTTP_200_OK
        cookie = response.cookies.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        assert cookie.value == ""
        assert cookie['max-age'] == 0

    def test_protected_endpoint_without_cookie(self, client):
        url = reverse('protected')
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_with_cookie(self, client):
        self.User.objects.create_user(username="cookieuser", password="TestPassword123!")

        login_url = reverse('login')
        login_response = client.post(
            login_url,
            {"username": "cookieuser", "password": "TestPassword123!"}
        )
        assert login_response.status_code == status.HTTP_200_OK

        protected_url = reverse('protected')
        response = client.get(protected_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "cookieuser"
