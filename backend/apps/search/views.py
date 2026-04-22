from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions

from .filters import SearchFilter
from .models import Search
from .serializers import SearchSerializer


class SearchListCreateView(generics.ListCreateAPIView):
    serializer_class = SearchSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SearchFilter
    ordering = ("-created_at",)

    def get_queryset(self):
        return Search.objects.filter(user=self.request.user).order_by("-created_at")


class SearchDetailView(generics.RetrieveAPIView):
    serializer_class = SearchSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Search.objects.filter(user=self.request.user)
