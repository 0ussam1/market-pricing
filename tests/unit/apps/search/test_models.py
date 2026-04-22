import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.search.models import (
    AnalysisResult,
    AssociationRule,
    RawPrice,
    Search,
    SearchAnalysis,
)


@pytest.mark.django_db
class TestSearchModels:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = get_user_model().objects.create_user(
            username="search-user",
            email="search@example.com",
            password="StrongPassword123!",
        )

    def create_search(self):
        return Search.objects.create(
            user=self.user,
            query="iphone 15",
            platforms=["amazon", "ebay"],
            status=Search.Status.PENDING,
        )

    def create_raw_price(self, search, url="https://example.com/item-1"):
        return RawPrice.objects.create(
            search=search,
            platform="amazon",
            title="iPhone 15",
            price="999.99",
            currency="USD",
            exchange_rate=1.0,
            url=url,
            seller_rating=4.5,
            condition=RawPrice.Condition.NEW,
        )

    def test_create_each_model(self):
        search = self.create_search()
        raw_price = self.create_raw_price(search)
        analysis_result = AnalysisResult.objects.create(
            raw_price=raw_price,
            cluster_kmeans=1,
            cluster_dbscan=2,
            is_anomaly=False,
            deal_score=0.82,
            pca_x=1.2,
            pca_y=3.4,
        )
        search_analysis = SearchAnalysis.objects.create(
            search=search,
            stats={"avg_price": 999.99},
            best_deal=raw_price,
        )
        association_rule = AssociationRule.objects.create(
            search=search,
            antecedent=["amazon"],
            consequent=["new"],
            support=0.4,
            confidence=0.8,
            lift=1.2,
        )

        assert Search.objects.count() == 1
        assert RawPrice.objects.count() == 1
        assert AnalysisResult.objects.count() == 1
        assert SearchAnalysis.objects.count() == 1
        assert AssociationRule.objects.count() == 1
        assert analysis_result.raw_price == raw_price
        assert search_analysis.best_deal == raw_price
        assert association_rule.search == search

    def test_cascade_delete_removes_children(self):
        search = self.create_search()
        raw_price = self.create_raw_price(search)
        AnalysisResult.objects.create(raw_price=raw_price)
        SearchAnalysis.objects.create(search=search, stats={"count": 1}, best_deal=raw_price)
        AssociationRule.objects.create(
            search=search,
            antecedent=["amazon"],
            consequent=["used"],
            support=0.2,
            confidence=0.5,
            lift=1.1,
        )

        search.delete()

        assert Search.objects.count() == 0
        assert RawPrice.objects.count() == 0
        assert AnalysisResult.objects.count() == 0
        assert SearchAnalysis.objects.count() == 0
        assert AssociationRule.objects.count() == 0

    def test_unique_together_duplicate_search_url_raises_integrity_error(self):
        search = self.create_search()
        self.create_raw_price(search, url="https://example.com/duplicate")

        with pytest.raises(IntegrityError):
            RawPrice.objects.create(
                search=search,
                platform="ebay",
                title="Duplicate listing",
                price="950.00",
                currency="USD",
                exchange_rate=1.0,
                url="https://example.com/duplicate",
            )
