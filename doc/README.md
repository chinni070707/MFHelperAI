# 🚀 MFHelper - Mutual Fund Portfolio Analytics SaaS

A comprehensive SaaS platform for mutual fund portfolio tracking, analysis, and insights.

## 📋 Features

- **📁 Multiple Data Import Options**
  - Excel/CSV upload with flexible column mapping
  - CAS PDF parsing (CAMS/KFintech Consolidated Account Statement)
  - API integration ready (CAMS, KFintech, MFU)
  
- **📊 Portfolio Analytics**
  - Market cap allocation (Large/Mid/Small)
  - AMC-wise distribution with interactive charts
  - Investment style analysis (GARP, Momentum, Value, etc.)
  - Performance tracking with returns %
  
- **🎯 Rebalancing Tools**
  - Target allocation calculator
  - Fresh investment planner
  - Tax-aware rebalancing suggestions
  
- **📈 Risk Metrics**
  - Alpha tracking
  - Category-wise performance
  - Gain/Loss analysis

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 3. Open in Browser

- **Landing Page**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

## 📁 Data Import Options

### Option 1: Excel Upload
Upload your portfolio in Excel format with these columns:
- `Fund Name` (required)
- `AMC` / `Fund House`
- `Category` (Large Cap, Mid Cap, Small Cap, etc.)
- `Invested` / `Amount Invested`
- `Current Value`
- `1Y Return`, `3Y Return`, `Alpha` (optional)
- `Style` (GARP, Momentum, Quality, Value, etc.)

### Option 2: CAS PDF Upload
Upload your Consolidated Account Statement (CAS) from CAMS or KFintech:
1. Visit [CAMS Online](https://www.camsonline.com) or [KFintech](https://mfs.kfintech.com)
2. Request CAS statement (it's free)
3. PDF will be emailed within minutes
4. Upload the PDF (password is your PAN)

## 🏗️ Project Structure

```
MFHelper/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database setup
│   │   ├── models/              # Database models
│   │   └── routes/              # API endpoints
│   │       ├── upload.py        # Excel & CAS upload
│   │       ├── portfolio.py     # Portfolio management
│   │       ├── analytics.py     # Analytics endpoints
│   │       └── rebalance.py     # Rebalancing calculator
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Landing page with upload options
│   └── dashboard.html           # Portfolio dashboard
│   ├── js/
│   └── assets/
├── data/
│   ├── fund_master.json         # Fund metadata
│   └── amc_master.json          # AMC information
├── tests/
├── docker-compose.yml
└── .env.example
```

## 🚀 Quick Start

### Option 1: Run with Python

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r backend/requirements.txt

# Run the server
cd backend
uvicorn app.main:app --reload --port 8000
```

### Option 2: Run with Docker

```bash
docker-compose up -d
```

Open http://localhost:8000 in your browser.

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/excel` | POST | Upload Excel portfolio |
| `/api/upload/cas` | POST | Upload CAS PDF |
| `/api/portfolio/{user_id}` | GET | Get portfolio data |
| `/api/analytics/{user_id}` | GET | Get analytics |
| `/api/rebalance` | POST | Calculate rebalancing |

## 🔐 RTA API Integration

To integrate with CAMS/KFintech APIs:

1. Register as SEBI RIA or AMFI MFD
2. Apply for API credentials
3. Configure in `.env` file

See `docs/RTA_INTEGRATION.md` for detailed guide.

## 📄 License

MIT License - See LICENSE file
