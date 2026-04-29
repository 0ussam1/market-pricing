from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .filters import SearchFilter
from .models import Search
from .serializers import (
    SearchCreateSerializer,
    SearchListSerializer,
    SearchSerializer,
    SearchStatusSerializer,
)
from .tasks import run_search_pipeline


class SearchListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SearchFilter

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SearchCreateSerializer
        return SearchListSerializer

    def get_queryset(self):
        return Search.objects.filter(user=self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data["query"]
        platforms = serializer.validated_data["platforms"]

        # 1. Deduplication Logic
        # Filter by user, query and active status first (fast database query)
        potential_searches = Search.objects.filter(
            user=request.user,
            query__iexact=query,
            status__in=[Search.Status.PENDING, Search.Status.PROCESSING]
        )
        
        # Check platforms in Python to ensure SQLite compatibility (JSONField __contains not supported)
        existing_search = None
        target_platforms = sorted(platforms)
        for s in potential_searches:
            if sorted(s.platforms) == target_platforms:
                existing_search = s
                break

        if existing_search:
            # Return existing search with 200 OK
            out_serializer = SearchCreateSerializer(existing_search)
            return Response(out_serializer.data, status=status.HTTP_200_OK)

        # 2. Create new search
        search = serializer.save(user=request.user, status=Search.Status.PENDING)
        
        # 3. Dispatch Celery Task
        run_search_pipeline.delay(search.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SearchDetailView(generics.RetrieveAPIView):
    serializer_class = SearchSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Search.objects.filter(user=self.request.user)


class SearchStatusView(generics.RetrieveAPIView):
    serializer_class = SearchStatusSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Search.objects.filter(user=self.request.user)
