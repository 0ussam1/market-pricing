from django.urls import path

from .views import SearchDetailView, SearchListCreateView

urlpatterns = [
    path("", SearchListCreateView.as_view(), name="search-list-create"),
    path("<int:pk>/", SearchDetailView.as_view(), name="search-detail"),
]
