from rest_framework import serializers

from .models import Search


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = (
            "id",
            "user",
            "query",
            "platforms",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "status", "created_at", "updated_at")

    def validate_platforms(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Platforms must be a non-empty list.")

        cleaned_platforms = []
        for platform in value:
            if not isinstance(platform, str) or not platform.strip():
                raise serializers.ValidationError(
                    "Each platform must be a non-empty string."
                )
            cleaned_platforms.append(platform.strip())

        return cleaned_platforms

    def create(self, validated_data):
        return Search.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )
