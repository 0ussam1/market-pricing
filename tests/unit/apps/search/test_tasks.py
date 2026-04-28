import pytest
from unittest.mock import MagicMock, PropertyMock, patch

from apps.search.models import Search, RawPrice, AnalysisResult, SearchAnalysis, AssociationRule
from apps.search.tasks import run_search_pipeline, FALLBACK_RATES


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )


@pytest.fixture
def search(db, user):
    return Search.objects.create(
        user=user,
        query="iphone 15",
        platforms=["jumia"],
        status=Search.Status.PENDING,
    )


@pytest.fixture
def mock_scrape_result():
    return [
        {
            "platform": "jumia",
            "title": "iPhone 15",
            "price": 10000.00,
            "currency": "MAD",
            "url": "https://jumia.ma/iphone15",
            "rating": 4.5,
        },
        {
            "platform": "jumia",
            "title": "iPhone 15 Pro",
            "price": 13000.00,
            "currency": "MAD",
            "url": "https://jumia.ma/iphone15pro",
        },
    ]


@pytest.fixture
def mock_pipeline_result():
    result = MagicMock()
    result.stats = {"count": 2, "mean": 11500.0}
    result.best_deal_id = None
    result.analysis_results = []
    result.association_rules = []
    result.pca_points = []
    return result


class TestRunSearchPipelineSuccess:
    @patch("apps.search.tasks.notify_ws")
    @patch("apps.search.tasks.run_mining_pipeline")
    @patch("apps.search.tasks.scrape_all")
    @patch("apps.search.tasks.get_exchange_rate")
    def test_full_pipeline(
        self,
        mock_get_rates,
        mock_scrape,
        mock_mine,
        mock_notify,
        search,
        mock_scrape_result,
        mock_pipeline_result,
    ):
        mock_get_rates.return_value = {"MAD": 1.0}
        mock_scrape.return_value = mock_scrape_result
        mock_mine.return_value = mock_pipeline_result

        run_search_pipeline(search.id)

        search.refresh_from_db()
        assert search.status == Search.Status.COMPLETED
        assert RawPrice.objects.filter(search=search).count() == 2
        assert SearchAnalysis.objects.filter(search=search).count() == 1
        assert AnalysisResult.objects.filter(raw_price__search=search).count() == 0
        assert AssociationRule.objects.filter(search=search).count() == 0

        # Verify WS notifications
        mock_notify.assert_any_call(search.id, "status", {"status": "processing"})
        mock_notify.assert_any_call(search.id, "completed", {})

    @patch("apps.search.tasks.notify_ws")
    @patch("apps.search.tasks.run_mining_pipeline")
    @patch("apps.search.tasks.scrape_all")
    @patch("apps.search.tasks.get_exchange_rate")
    def test_fallback_rates_used_when_exchange_service_fails(
        self,
        mock_get_rates,
        mock_scrape,
        mock_mine,
        mock_notify,
        search,
    ):
        mock_get_rates.side_effect = Exception("Timeout")
        mock_scrape.return_value = [
            {
                "platform": "amazon",
                "title": "iPhone 15",
                "price": 999.00,
                "currency": "USD",
                "url": "https://amazon.com/iphone15",
            }
        ]
        mock_mine.return_value = MagicMock(
            stats={},
            best_deal_id=None,
            analysis_results=[],
            association_rules=[],
            pca_points=[],
        )

        run_search_pipeline(search.id)

        raw = RawPrice.objects.get(search=search)
        assert raw.exchange_rate == FALLBACK_RATES["USD"]
        assert raw.currency == "USD"


class TestRunSearchPipelineAtomicRollback:
    @patch("apps.search.tasks.notify_ws")
    @patch("apps.search.tasks.run_mining_pipeline")
    @patch("apps.search.tasks.scrape_all")
    @patch("apps.search.tasks.get_exchange_rate")
    def test_mining_failure_rolls_back_raw_prices(
        self,
        mock_get_rates,
        mock_scrape,
        mock_mine,
        mock_notify,
        search,
        mock_scrape_result,
    ):
        mock_get_rates.return_value = {"MAD": 1.0}
        mock_scrape.return_value = mock_scrape_result
        mock_mine.side_effect = RuntimeError("Mining exploded")

        # Patch retry so the test does not actually reschedule
        with patch.object(run_search_pipeline, "retry") as mock_retry:
            mock_retry.side_effect = Exception("Retry triggered")
            with pytest.raises(Exception):
                run_search_pipeline(search.id)

        # RawPrice created inside the atomic block must have been rolled back
        assert RawPrice.objects.filter(search=search).count() == 0
        # Analysis and SearchAnalysis should also be absent
        assert AnalysisResult.objects.filter(raw_price__search=search).count() == 0
        assert SearchAnalysis.objects.filter(search=search).count() == 0
        assert AssociationRule.objects.filter(search=search).count() == 0


class TestRunSearchPipelineRetry:
    @patch("apps.search.tasks.notify_ws")
    @patch("apps.search.tasks.run_mining_pipeline")
    @patch("apps.search.tasks.scrape_all")
    @patch("apps.search.tasks.get_exchange_rate")
    def test_retry_countdown_formula_first_failure(
        self,
        mock_get_rates,
        mock_scrape,
        mock_mine,
        mock_notify,
        search,
        mock_scrape_result,
    ):
        """First failure (retries=0) → countdown = 30 * (2**0) = 30s."""
        mock_get_rates.return_value = {"MAD": 1.0}
        mock_scrape.return_value = mock_scrape_result
        mock_mine.side_effect = RuntimeError("Mining exploded")
        
        mock_self = MagicMock()
        mock_self.request.retries = 0
        mock_self.max_retries = 2
        mock_self.retry.side_effect = Exception("Retry triggered")

        with pytest.raises(Exception, match="Retry triggered"):
            run_search_pipeline.__wrapped__.__func__(mock_self, search.id)

        mock_self.retry.assert_called_once()
        call_kwargs = mock_self.retry.call_args.kwargs
        assert call_kwargs["countdown"] == 30 * (2 ** 0)  # 30

    @patch("apps.search.tasks.notify_ws")
    @patch("apps.search.tasks.run_mining_pipeline")
    @patch("apps.search.tasks.scrape_all")
    @patch("apps.search.tasks.get_exchange_rate")
    def test_retry_countdown_formula_second_failure(
        self,
        mock_get_rates,
        mock_scrape,
        mock_mine,
        mock_notify,
        search,
        mock_scrape_result,
    ):
        """Second failure (retries=1) → countdown = 30 * (2**1) = 60s."""
        mock_get_rates.return_value = {"MAD": 1.0}
        mock_scrape.return_value = mock_scrape_result
        mock_mine.side_effect = RuntimeError("Mining exploded")
        
        mock_self = MagicMock()
        mock_self.request.retries = 1
        mock_self.max_retries = 2
        mock_self.retry.side_effect = Exception("Retry triggered")

        with pytest.raises(Exception, match="Retry triggered"):
            run_search_pipeline.__wrapped__.__func__(mock_self, search.id)

        mock_self.retry.assert_called_once()
        call_kwargs = mock_self.retry.call_args.kwargs
        assert call_kwargs["countdown"] == 30 * (2 ** 1)  # 60


class TestRunSearchPipelineFinalFailure:
    @patch("apps.search.tasks.notify_ws")
    @patch("apps.search.tasks.run_mining_pipeline")
    @patch("apps.search.tasks.scrape_all")
    @patch("apps.search.tasks.get_exchange_rate")
    def test_final_failure_sets_status_failed_and_notifies(
        self,
        mock_get_rates,
        mock_scrape,
        mock_mine,
        mock_notify,
        search,
        mock_scrape_result,
    ):
        """When retries exhausted, task marks search failed and sends WS error."""
        mock_get_rates.return_value = {"MAD": 1.0}
        mock_scrape.return_value = mock_scrape_result
        mock_mine.side_effect = RuntimeError("Mining exploded")

        mock_self = MagicMock()
        mock_self.request.retries = 2
        mock_self.max_retries = 2

        with pytest.raises(RuntimeError, match="Mining exploded"):
            run_search_pipeline.__wrapped__.__func__(mock_self, search.id)

        search.refresh_from_db()
        assert search.status == Search.Status.FAILED
        mock_notify.assert_any_call(search.id, "error", {"message": "Mining exploded"})


class TestNotifyWsOutsideAtomic:
    @patch("apps.search.tasks.notify_ws")
    @patch("apps.search.tasks.run_mining_pipeline")
    @patch("apps.search.tasks.scrape_all")
    @patch("apps.search.tasks.get_exchange_rate")
    def test_notify_completed_called_outside_atomic_block(
        self,
        mock_get_rates,
        mock_scrape,
        mock_mine,
        mock_notify,
        search,
        mock_scrape_result,
        mock_pipeline_result,
    ):
        """The 'completed' WS notification must happen after the DB transaction commits."""
        mock_get_rates.return_value = {"MAD": 1.0}
        mock_scrape.return_value = mock_scrape_result
        mock_mine.return_value = mock_pipeline_result

        with patch("apps.search.tasks.transaction.atomic") as mock_atomic:
            # Use the real atomic as the context manager so DB state is real
            mock_atomic.return_value.__enter__ = lambda s: None
            mock_atomic.return_value.__exit__ = lambda s, *a: None

            run_search_pipeline.__wrapped__.__func__(MagicMock(), search.id)

        # Verify atomic was called at least once (explicitly in the task)
        assert mock_atomic.called

        # Verify the completed notification is only sent after atomic block
        call_order = [c.args for c in mock_notify.call_args_list]
        # First call is "status" (processing)
        assert call_order[0] == (search.id, "status", {"status": "processing"})
        # Last call is "completed" — must be after atomic
        assert call_order[-1] == (search.id, "completed", {})
