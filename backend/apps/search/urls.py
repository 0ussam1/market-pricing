from django.urls import path

from .views import SearchDetailView, SearchListCreateView, SearchStatusView

urlpatterns = [
    path("", SearchListCreateView.as_view(), name="search-list-create"),
    path("<int:pk>/", SearchDetailView.as_view(), name="search-detail"),
    path("<int:pk>/status/", SearchStatusView.as_view(), name="search-status"),
]
