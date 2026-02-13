"""
Tests for CAS Upload → Dashboard Data Flow

Verifies that after CAS PDF upload:
1. Data is correctly saved to database (Portfolio + Holdings)
2. Dashboard API (/api/portfolio/) returns the saved data correctly
3. Import summary provides diagnostic info for debugging
4. Total invested/current values are non-zero when parsed correctly
5. CAS import summary endpoint works for verification
"""
import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from app.models.models import Portfolio, Holding


# ============ Fixtures ============

@pytest.fixture
def sample_cas_holdings():
    """Sample CAS holdings data as returned by parse_cas_pdf()"""
    return [
        {
            'fund_name': 'HDFC Mid-Cap Opportunities Fund Direct Growth',
            'folio': '12345678',
            'amc': 'HDFC AMC',
            'category': 'Mid Cap',
            'style': 'Quality',
            'units': 150.123,
            'nav': 456.78,
            'invested': 50000.0,
            'current_value': 68567.0,
            'return_1y': '-',
            'return_3y': '-',
            'alpha': '-'
        },
        {
            'fund_name': 'Parag Parikh Flexi Cap Fund Direct Growth',
            'folio': '87654321',
            'amc': 'PPFAS AMC',
            'category': 'Flexi Cap',
            'style': 'GARP',
            'units': 200.456,
            'nav': 678.90,
            'invested': 100000.0,
            'current_value': 136035.0,
            'return_1y': '-',
            'return_3y': '-',
            'alpha': '-'
        },
        {
            'fund_name': 'ICICI Prudential Bluechip Fund Direct Growth',
            'folio': '11223344',
            'amc': 'ICICI Prudential',
            'category': 'Large Cap',
            'style': 'Quality',
            'units': 500.789,
            'nav': 89.12,
            'invested': 35000.0,
            'current_value': 44612.0,
            'return_1y': '-',
            'return_3y': '-',
            'alpha': '-'
        }
    ]


@pytest.fixture
def sample_cas_result(sample_cas_holdings):
    """Complete parse_cas_pdf result"""
    total_invested = sum(h['invested'] for h in sample_cas_holdings)
    total_current = sum(h['current_value'] for h in sample_cas_holdings)
    return {
        'success': True,
        'source': 'cas_pdf',
        'holdings': sample_cas_holdings,
        'summary': {
            'total_funds': len(sample_cas_holdings),
            'total_invested': total_invested,
            'total_current': total_current,
            'total_gain': total_current - total_invested,
            'return_pct': (total_current - total_invested) / total_invested * 100
        },
        'parsed_at': '2026-02-13T10:00:00'
    }


@pytest.fixture
def cas_zero_invested_holdings():
    """CAS holdings where invested amount is 0 (parsing failure scenario)"""
    return [
        {
            'fund_name': 'SBI Small Cap Fund Direct Growth',
            'folio': '99887766',
            'amc': 'SBI Mutual Fund',
            'category': 'Small Cap',
            'style': 'Blend',
            'units': 100.0,
            'nav': 150.0,
            'invested': 0,  # Parser failed to extract cost
            'current_value': 15000.0,
            'return_1y': '-',
            'return_3y': '-',
            'alpha': '-'
        }
    ]


@pytest.fixture
def cas_estimated_cost_holdings():
    """CAS holdings where invested is estimated (fallback parser: invested = current_value * 0.9)"""
    return [
        {
            'fund_name': 'Axis Bluechip Fund Direct Growth',
            'folio': '55667788',
            'amc': 'Axis AMC',
            'category': 'Large Cap',
            'style': 'Quality',
            'units': 0,
            'nav': 0,
            'invested': 90000.0,  # = 100000 * 0.9 (estimated)
            'current_value': 100000.0,
            'return_1y': '-',
            'return_3y': '-',
            'alpha': '-'
        }
    ]


# ============ Test CAS Upload → DB Save ============

class TestCASUploadSavesToDatabase:
    """Test that CAS upload correctly saves data to the database"""

    def test_cas_upload_saves_portfolio_with_correct_totals(
        self, authenticated_client, sample_cas_result, db_session
    ):
        """CAS upload should create a Portfolio record with correct total_invested and total_current"""
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            # Create a minimal valid PDF
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            response = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['saved_to_database'] is True
        assert data['portfolio_id'] is not None
        
        # Verify in database
        portfolio = db_session.query(Portfolio).filter(
            Portfolio.id == data['portfolio_id']
        ).first()
        
        assert portfolio is not None
        assert portfolio.source == 'cas_pdf'
        assert portfolio.total_invested == pytest.approx(185000.0)  # 50000 + 100000 + 35000
        assert portfolio.total_current == pytest.approx(249214.0)   # 68567 + 136035 + 44612
        assert portfolio.total_gain == pytest.approx(249214.0 - 185000.0)

    def test_cas_upload_saves_all_holdings(
        self, authenticated_client, sample_cas_result, db_session
    ):
        """CAS upload should create Holding records for each fund"""
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            response = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        data = response.json()
        portfolio_id = data['portfolio_id']
        
        holdings = db_session.query(Holding).filter(
            Holding.portfolio_id == portfolio_id
        ).all()
        
        assert len(holdings) == 3
        
        # Verify each holding has correct data
        hdfc = next(h for h in holdings if 'HDFC' in h.fund_name)
        assert hdfc.invested_amount == pytest.approx(50000.0)
        assert hdfc.current_value == pytest.approx(68567.0)
        assert hdfc.units == pytest.approx(150.123)
        assert hdfc.amc == 'HDFC AMC'
        assert hdfc.category == 'Mid Cap'
        
        ppfas = next(h for h in holdings if 'Parag Parikh' in h.fund_name)
        assert ppfas.invested_amount == pytest.approx(100000.0)
        assert ppfas.current_value == pytest.approx(136035.0)

    def test_cas_upload_returns_import_summary(
        self, authenticated_client, sample_cas_result
    ):
        """CAS upload should return import_summary with detailed diagnostic info"""
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            response = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        data = response.json()
        assert 'import_summary' in data
        
        summary = data['import_summary']
        assert summary['total_funds_parsed'] == 3
        assert summary['total_invested'] == pytest.approx(185000.0)
        assert summary['total_current'] == pytest.approx(249214.0)
        assert 'HDFC AMC' in summary['amcs_found']
        assert 'PPFAS AMC' in summary['amcs_found']
        assert 'Mid Cap' in summary['categories_found']
        assert summary['funds_with_zero_invested'] == 0
        assert len(summary['warnings']) == 0
        
        # Verify holdings_detail
        assert len(summary['holdings_detail']) == 3
        for hd in summary['holdings_detail']:
            assert 'fund_name' in hd
            assert 'invested' in hd
            assert 'current_value' in hd
            assert 'warnings' in hd

    def test_cas_upload_import_summary_has_verification(
        self, authenticated_client, sample_cas_result
    ):
        """CAS upload import_summary should include DB verification data"""
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            response = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        data = response.json()
        summary = data['import_summary']
        
        assert 'verification' in summary
        v = summary['verification']
        assert v['portfolio_found'] is True
        assert v['holdings_saved_count'] == 3
        assert v['holdings_with_invested_gt_zero'] == 3
        assert v['holdings_with_current_gt_zero'] == 3
        assert v['portfolio_total_invested'] == pytest.approx(185000.0)
        assert v['portfolio_total_current'] == pytest.approx(249214.0)


# ============ Test CAS Upload → Dashboard Retrieval ============

class TestCASUploadToDashboard:
    """Test the complete CAS upload → dashboard data retrieval flow"""

    def test_dashboard_shows_correct_invested_after_cas_upload(
        self, authenticated_client, sample_cas_result
    ):
        """After CAS upload, GET /api/portfolio/ should return correct total_invested (not 0.00L)"""
        # Step 1: Upload CAS
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            upload_response = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        assert upload_response.status_code == 200
        assert upload_response.json()['saved_to_database'] is True
        
        # Step 2: Fetch portfolio (what dashboard does)
        portfolio_response = authenticated_client.get("/api/portfolio/")
        assert portfolio_response.status_code == 200
        
        portfolio_data = portfolio_response.json()
        
        # Step 3: Verify the data that dashboard would render
        assert len(portfolio_data['holdings']) == 3
        assert portfolio_data['summary']['total_invested'] == pytest.approx(185000.0)
        assert portfolio_data['summary']['total_current'] == pytest.approx(249214.0)
        assert portfolio_data['summary']['total_invested'] > 0, \
            "Dashboard should NOT show ₹0.00L invested after CAS upload"
        assert portfolio_data['summary']['total_current'] > 0
        assert portfolio_data['summary']['total_gain'] == pytest.approx(249214.0 - 185000.0)
        
    def test_dashboard_holdings_have_invested_amounts(
        self, authenticated_client, sample_cas_result
    ):
        """Each holding returned to dashboard should have non-zero invested amount"""
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        portfolio_data = authenticated_client.get("/api/portfolio/").json()
        
        for holding in portfolio_data['holdings']:
            assert holding['invested'] > 0, \
                f"Holding '{holding['fund_name']}' has ₹0 invested — CAS data not saved correctly"
            assert holding['current_value'] > 0
            assert holding['fund_name'] != ''

    def test_dashboard_holdings_preserve_amc_and_category(
        self, authenticated_client, sample_cas_result
    ):
        """Holdings returned to dashboard should have correct AMC and category from CAS"""
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        portfolio_data = authenticated_client.get("/api/portfolio/").json()
        
        fund_names = [h['fund_name'] for h in portfolio_data['holdings']]
        assert any('HDFC' in name for name in fund_names)
        assert any('Parag Parikh' in name for name in fund_names)
        
        # Check AMCs are preserved
        amcs = [h['amc'] for h in portfolio_data['holdings']]
        assert 'HDFC AMC' in amcs
        assert 'PPFAS AMC' in amcs
        
        # Check categories
        categories = [h['category'] for h in portfolio_data['holdings']]
        assert 'Mid Cap' in categories
        assert 'Flexi Cap' in categories


# ============ Test CAS Import Summary Endpoint ============

class TestCASImportSummaryEndpoint:
    """Test GET /api/portfolio/cas-import-summary"""

    def test_cas_import_summary_empty_portfolio(self, authenticated_client):
        """CAS import summary should indicate no data when portfolio is empty"""
        response = authenticated_client.get("/api/portfolio/cas-import-summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data['has_data'] is False
        assert 'message' in data

    def test_cas_import_summary_after_upload(
        self, authenticated_client, sample_cas_result
    ):
        """CAS import summary should show correct data after upload"""
        # Upload CAS
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        # Get summary
        response = authenticated_client.get("/api/portfolio/cas-import-summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data['has_data'] is True
        assert data['total_funds'] == 3
        assert data['total_invested'] == pytest.approx(185000.0)
        assert data['total_current'] == pytest.approx(249214.0)
        assert data['source'] == 'cas_pdf'
        assert 'HDFC AMC' in data['amcs']
        assert data['funds_with_zero_invested'] == 0
        assert len(data['warnings']) == 0
        
        # Verify holdings detail
        assert len(data['holdings']) == 3
        for h in data['holdings']:
            assert h['has_invested']
            assert h['has_current_value']


# ============ Test Edge Cases ============

class TestCASUploadEdgeCases:
    """Test edge cases in CAS upload → dashboard flow"""

    def test_cas_upload_with_zero_invested_warns(
        self, authenticated_client, cas_zero_invested_holdings
    ):
        """CAS upload with zero invested amounts should include warnings"""
        result = {
            'success': True,
            'source': 'cas_pdf',
            'holdings': cas_zero_invested_holdings,
            'summary': {
                'total_funds': 1,
                'total_invested': 0,
                'total_current': 15000.0,
                'total_gain': 15000.0,
                'return_pct': 0
            },
            'parsed_at': '2026-02-13T10:00:00'
        }
        
        with patch('app.routes.upload.parse_cas_pdf', return_value=result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            response = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        data = response.json()
        summary = data['import_summary']
        
        assert summary['funds_with_zero_invested'] == 1
        assert any('₹0 invested' in w for w in summary['warnings'])
        
        # Dashboard should still show the portfolio (with 0 invested)
        portfolio_data = authenticated_client.get("/api/portfolio/").json()
        assert len(portfolio_data['holdings']) == 1
        assert portfolio_data['summary']['total_current'] == pytest.approx(15000.0)

    def test_cas_upload_with_estimated_cost_warns(
        self, authenticated_client, cas_estimated_cost_holdings
    ):
        """CAS upload with estimated costs (fallback parser) should include warnings"""
        result = {
            'success': True,
            'source': 'cas_pdf',
            'holdings': cas_estimated_cost_holdings,
            'summary': {
                'total_funds': 1,
                'total_invested': 90000.0,
                'total_current': 100000.0,
                'total_gain': 10000.0,
                'return_pct': 11.11
            },
            'parsed_at': '2026-02-13T10:00:00'
        }
        
        with patch('app.routes.upload.parse_cas_pdf', return_value=result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            response = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        data = response.json()
        summary = data['import_summary']
        
        assert summary['funds_with_estimated_cost'] == 1
        assert any('estimated' in w for w in summary['warnings'])

    def test_cas_upload_unauthenticated_returns_summary_but_not_saved(
        self, client, sample_cas_result
    ):
        """CAS upload without auth should still return import_summary but not save to DB"""
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            response = client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['saved_to_database'] is False
        assert 'import_summary' in data
        assert data['import_summary']['total_funds_parsed'] == 3
        assert data['import_summary']['saved_to_database'] is False

    def test_multiple_cas_uploads_use_latest(
        self, authenticated_client, sample_cas_result
    ):
        """Multiple CAS uploads should keep old portfolios; dashboard shows newest"""
        # First upload
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            resp1 = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas1.pdf", pdf_bytes, "application/pdf")}
            )
        
        first_portfolio_id = resp1.json()['portfolio_id']
        
        # Verify first upload exists
        portfolio_data = authenticated_client.get("/api/portfolio/").json()
        assert len(portfolio_data['holdings']) == 3  # sample_cas_result has 3 holdings
        
        # Second upload with different data
        modified_result = {
            'success': True,
            'source': 'cas_pdf',
            'holdings': [
                {
                    'fund_name': 'SBI Small Cap Fund Direct Growth',
                    'folio': '99887766',
                    'amc': 'SBI Mutual Fund',
                    'category': 'Small Cap',
                    'style': 'Blend',
                    'units': 500.0,
                    'nav': 100.0,
                    'invested': 40000.0,
                    'current_value': 50000.0,
                    'return_1y': '-',
                    'return_3y': '-',
                    'alpha': '-'
                }
            ],
            'summary': {
                'total_funds': 1,
                'total_invested': 40000.0,
                'total_current': 50000.0,
                'total_gain': 10000.0,
                'return_pct': 25.0
            },
            'parsed_at': '2026-02-13T11:00:00'
        }
        
        with patch('app.routes.upload.parse_cas_pdf', return_value=modified_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content 2")
            resp2 = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas2.pdf", pdf_bytes, "application/pdf")}
            )
        
        second_portfolio_id = resp2.json()['portfolio_id']
        assert second_portfolio_id != first_portfolio_id  # Both portfolios kept
        
        # Dashboard should show the latest upload (the newer one)
        portfolio_data = authenticated_client.get("/api/portfolio/").json()
        assert len(portfolio_data['holdings']) == 1
        assert portfolio_data['summary']['total_invested'] == pytest.approx(40000.0)
        assert portfolio_data['holdings'][0]['fund_name'] == 'SBI Small Cap Fund Direct Growth'
        
        # History should show both portfolios preserved
        history = authenticated_client.get("/api/portfolio/history").json()
        assert history['total_count'] == 2
        assert history['snapshots'][0]['is_active'] is True  # Latest
        assert history['snapshots'][1]['is_active'] is False  # Old

    def test_portfolio_snapshot_endpoint(
        self, authenticated_client, sample_cas_result
    ):
        """GET /api/portfolio/snapshot/{id} returns the specific portfolio with holdings"""
        # Upload a portfolio
        with patch('app.routes.upload.parse_cas_pdf', return_value=sample_cas_result):
            pdf_bytes = BytesIO(b"%PDF-1.4\ntest content")
            resp = authenticated_client.post(
                "/api/upload/cas",
                files={"file": ("cas.pdf", pdf_bytes, "application/pdf")}
            )
        portfolio_id = resp.json()['portfolio_id']

        # Fetch the snapshot
        snap_resp = authenticated_client.get(f"/api/portfolio/snapshot/{portfolio_id}")
        assert snap_resp.status_code == 200
        data = snap_resp.json()
        assert data['portfolio_id'] == portfolio_id
        assert data['is_active'] is True
        assert len(data['holdings']) == 3
        assert data['summary']['total_invested'] == pytest.approx(185000.0)

    def test_portfolio_snapshot_not_found(self, authenticated_client):
        """GET /api/portfolio/snapshot/{bad_id} returns 404"""
        resp = authenticated_client.get("/api/portfolio/snapshot/99999")
        assert resp.status_code == 404


# ============ Test Import Summary Builder ============

class TestBuildCasImportSummary:
    """Test the _build_cas_import_summary helper function"""

    def test_summary_with_healthy_data(self):
        """Summary builder with all data present should have no warnings"""
        from app.routes.upload import _build_cas_import_summary
        
        result = {
            'holdings': [
                {'fund_name': 'Fund A', 'amc': 'AMC A', 'category': 'Large Cap',
                 'invested': 100000, 'current_value': 120000, 'units': 500, 'nav': 240},
                {'fund_name': 'Fund B', 'amc': 'AMC B', 'category': 'Mid Cap',
                 'invested': 50000, 'current_value': 60000, 'units': 200, 'nav': 300},
            ],
            'summary': {
                'total_invested': 150000,
                'total_current': 180000,
            }
        }
        
        summary = _build_cas_import_summary(result)
        
        assert summary['total_funds_parsed'] == 2
        assert summary['total_invested'] == 150000
        assert summary['total_current'] == 180000
        assert summary['funds_with_zero_invested'] == 0
        assert summary['funds_with_zero_current'] == 0
        assert summary['funds_with_estimated_cost'] == 0
        assert len(summary['warnings']) == 0
        assert 'AMC A' in summary['amcs_found']
        assert 'AMC B' in summary['amcs_found']

    def test_summary_with_zero_invested(self):
        """Summary builder should warn when holdings have zero invested"""
        from app.routes.upload import _build_cas_import_summary
        
        result = {
            'holdings': [
                {'fund_name': 'Fund A', 'amc': 'AMC A', 'category': 'Large Cap',
                 'invested': 0, 'current_value': 120000, 'units': 500, 'nav': 240},
            ],
            'summary': {'total_invested': 0, 'total_current': 120000}
        }
        
        summary = _build_cas_import_summary(result)
        
        assert summary['funds_with_zero_invested'] == 1
        assert len(summary['warnings']) > 0
        assert any('₹0 invested' in w for w in summary['warnings'])

    def test_summary_with_estimated_cost(self):
        """Summary builder should warn when invested is estimated (= value * 0.9)"""
        from app.routes.upload import _build_cas_import_summary
        
        result = {
            'holdings': [
                {'fund_name': 'Fund A', 'amc': 'AMC A', 'category': 'Large Cap',
                 'invested': 90000.0, 'current_value': 100000.0, 'units': 0, 'nav': 0},
            ],
            'summary': {'total_invested': 90000, 'total_current': 100000}
        }
        
        summary = _build_cas_import_summary(result)
        
        assert summary['funds_with_estimated_cost'] == 1
        assert any('estimated' in w for w in summary['warnings'])

    def test_summary_with_empty_holdings(self):
        """Summary builder with no holdings should warn"""
        from app.routes.upload import _build_cas_import_summary
        
        result = {
            'holdings': [],
            'summary': {'total_invested': 0, 'total_current': 0}
        }
        
        summary = _build_cas_import_summary(result)
        
        assert summary['total_funds_parsed'] == 0
        assert any('No holdings' in w for w in summary['warnings'])

    def test_summary_holdings_detail_includes_per_fund_warnings(self):
        """Each holding in holdings_detail should have per-holding warnings"""
        from app.routes.upload import _build_cas_import_summary
        
        result = {
            'holdings': [
                {'fund_name': 'Good Fund', 'amc': 'AMC A', 'category': 'Large Cap',
                 'invested': 100000, 'current_value': 120000, 'units': 500, 'nav': 240},
                {'fund_name': 'Bad Fund', 'amc': 'AMC B', 'category': 'Mid Cap',
                 'invested': 0, 'current_value': 0, 'units': 0, 'nav': 0},
            ],
            'summary': {'total_invested': 100000, 'total_current': 120000}
        }
        
        summary = _build_cas_import_summary(result)
        
        good_fund = next(h for h in summary['holdings_detail'] if h['fund_name'] == 'Good Fund')
        bad_fund = next(h for h in summary['holdings_detail'] if h['fund_name'] == 'Bad Fund')
        
        assert len(good_fund['warnings']) == 0
        assert 'invested_amount_is_zero' in bad_fund['warnings']
        assert 'current_value_is_zero' in bad_fund['warnings']
        assert 'units_is_zero' in bad_fund['warnings']
