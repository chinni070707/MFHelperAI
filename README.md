# MFHelper - Mutual Fund Portfolio Management Tool

> A comprehensive mutual fund portfolio analysis and management platform built with FastAPI and vanilla JavaScript.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Quick Start (For Your Colleague)

### Option 1: Automated Setup (Easiest)

**Windows (PowerShell):**
```powershell
# Run setup script (one-time)
.\setup.ps1

# Start servers
.\start.ps1
```

**Mac/Linux (Terminal):**
```bash
# Make scripts executable (one-time)
chmod +x setup.sh start.sh

# Run setup script (one-time)
./setup.sh

# Start servers
./start.sh
```

Then open: `http://localhost:3000`

### Option 2: Manual Setup

See **[QUICK_START.md](QUICK_START.md)** for detailed instructions (includes both Windows and Mac commands).

---

## ✨ Features

### 📊 Portfolio Management
- **Manual Entry**: Add funds manually with autocomplete
- **CAS Upload**: Import from CAMS/KFintech PDF statements
- **Excel/CSV Import**: Upload portfolio spreadsheets
- **Real-time Dashboard**: Track investments, gains, allocation

### 🔍 Analysis Tools
- **Overlap Analysis**: Check fund overlap (weight-based, sector HHI)
- **Risk Analysis**: Volatility, beta, Sharpe ratio, drawdown
- **Fund Comparison**: Side-by-side comparison of schemes
- **Rebalancing**: Calculate rebalance amounts to target allocation

### 🎯 Planning Tools
- **Goal Planning**: SIP, lumpsum calculators with inflation
- **Retirement Planner**: Calculate retirement corpus
- **Emergency Fund**: 3-6 month expense calculator

### 🔐 User Management
- **Authentication**: Email/password login
- **Guest Mode**: Auto-creates guest accounts for immediate access
- **Data Privacy**: All data stored in SQLite database

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **SQLite** - Embedded database
- **PyMuPDF** - PDF parsing for CAS uploads
- **Pandas** - Data processing

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Plotly.js** - Interactive charts
- **Chart.js** - Additional charting
- **HTML5/CSS3** - Modern responsive design

---

## 📂 Project Structure

```
MFHelper/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── routes/      # API endpoints
│   │   ├── utils/       # Utilities (auth, parsing)
│   │   └── main.py      # FastAPI app
│   ├── data/            # Fund holdings data
│   ├── alembic/         # Database migrations
│   └── requirements.txt
│
├── frontend/            # Static frontend
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript modules
│   ├── index.html      # Landing page
│   ├── dashboard.html  # Main dashboard
│   └── *.html          # Other pages
│
├── doc/                # Documentation
├── setup.ps1           # Setup script
├── start.ps1           # Start servers script
└── QUICK_START.md      # Detailed setup guide
```

---

## 🔧 Development

### Prerequisites
- Python 3.9+
- Node.js 16+ (optional)
- Git

### Backend Development

```powershell
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start with auto-reload
python -m uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Frontend Development

```powershell
cd frontend

# Start development server
python -m http.server 3000
```

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📊 Database

### Schema
- **users** - User accounts (authenticated + guest)
- **portfolios** - Portfolio snapshots
- **holdings** - Fund holdings per portfolio

### Migration Commands

```powershell
# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🧪 Testing

### Backend Tests
```powershell
cd backend
pytest
pytest -v --tb=short  # Verbose with short traceback
pytest tests/test_portfolio.py  # Specific test file
```

### Manual Testing
```powershell
# Verify database
python backend/get_all_users.py

# Check data storage
python backend/verify_database_storage.py
```

---

## 🚢 Deployment

### Render (Current)
- Configuration: `render.yaml`
- Startup: `startup.sh`
- Environment variables set in Render dashboard

### Other Platforms
1. Set environment variables (DATABASE_URL, SECRET_KEY)
2. Run migrations: `alembic upgrade head`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 🔒 Environment Variables

Create `.env` in `backend/`:

```env
# Database
DATABASE_URL=sqlite:///./mfhelper.db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS (for production)
ALLOWED_ORIGINS=https://yourdomain.com

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 📝 Recent Changes

✅ Guest user auto-creation for all entry methods
✅ Database storage for all users (no localStorage dependency)
✅ Manual entry pre-population on page revisit
✅ Dashboard data persistence monitoring
✅ Responsive overlap analysis charts (2-5 funds)

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 Support

- **Documentation**: [QUICK_START.md](QUICK_START.md)
- **Issues**: Check console logs (F12 → Console)
- **Database**: Run `python backend/get_all_users.py`
- **API**: Check `http://localhost:8000/docs`

---

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Real-time NAV updates
- [ ] Portfolio import from demat accounts
- [ ] Advanced backtesting
- [ ] AI-powered recommendations
- [ ] Multi-currency support

---

**Made with ❤️ for Indian mutual fund investors**
