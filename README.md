# Market Research & Pricing Analysis

A full-stack platform for real-time product price comparison and data-mining-powered insights across multiple e-commerce platforms.

## Overview

This platform searches products across multiple Moroccan and international e-commerce platforms (**Avito**, **Jumia**, **Amazon**, **eBay**, **AliExpress**), compares prices in real-time, and delivers actionable insights using advanced data mining techniques including clustering, anomaly detection, and association rule mining.

## Features

### Search & Scraping
- **Multi-platform scraping** with Playwright (dynamic) and Scrapy (static) engines
- **Supported platforms**: Avito, Jumia, Amazon, eBay, AliExpress
- **Real-time currency conversion** for cross-platform price comparison
- **Live progress tracking** via WebSocket (Django Channels)
- **Pagination support** for comprehensive result coverage

### Advanced Data Mining
- **Price Segmentation**: K-Means and DBSCAN clustering for market segment identification
- **Anomaly Detection**: Isolation Forest and Local Outlier Factor (LOF) for identifying pricing anomalies
- **Dimensionality Reduction**: PCA for 2D cluster visualization
- **Association Rule Mining**: Apriori and FP-Growth algorithms for discovering product relationships
- **Deal Scoring**: Custom scoring algorithm to identify the best deals

### Interactive Dashboard
- **Visual price distributions** with histograms and box plots
- **Cluster scatter maps** for market segmentation visualization
- **Association rules explorer** for product relationship discovery
- **Real-time results** with WebSocket live updates
- **Product comparison** tools
- **Price alerts** system
- **Analytics dashboard** with comprehensive statistics

### User Features
- **Authentication & Authorization** with JWT tokens
- **Search history** tracking and management
- **Export functionality** for search results
- **Responsive design** for desktop and mobile

## Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| Django | 5.1 | Web framework |
| Django REST Framework | 3.15 | REST API |
| PostgreSQL | 16 | Primary database |
| Celery | 5.4 | Task queue |
| Redis | 5.0 | Cache & message broker |
| Playwright | 1.56 | Dynamic web scraping |
| Scrapy | 2.11 | Static web scraping |
| Django Channels | 4.0 | WebSocket support |
| scikit-learn | 1.5 | Machine learning |
| mlxtend | 0.23 | Association rules |
| Pandas | 2.2 | Data manipulation |
| NumPy | 1.26 | Numerical computing |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3 | UI framework |
| Vite | 5.4 | Build tool |
| Chart.js | 4.5 | Charting library |
| D3.js | 7.9 | Data visualization |
| Recharts | 3.8 | Composable charts |
| React Router | 6.30 | Client-side routing |
| Axios | 1.15 | HTTP client |
| Lucide React | 1.8 | Icon library |

### Infrastructure
- **Docker & Docker Compose** for containerization
- **Gunicorn** for production WSGI server
- **Nginx** for reverse proxy and static file serving
- **Daphne** for ASGI/WebSocket server

## Project Structure

```
.
├── backend/                    # Django application
│   ├── apps/                   # Django apps
│   │   ├── authentication/     # User auth (JWT, login, register)
│   │   ├── search/             # Search, filters, models, tasks
│   │   ├── export/             # Data export functionality
│   │   └── ws/                 # WebSocket consumers
│   ├── config/                 # Django settings (dev, prod, test)
│   ├── mining/                 # Data mining modules
│   │   ├── anomaly.py          # Isolation Forest, LOF
│   │   ├── association.py      # Apriori, FP-Growth
│   │   ├── clustering.py       # K-Means, DBSCAN
│   │   ├── pca.py              # Principal Component Analysis
│   │   ├── pipeline.py         # Mining pipeline orchestration
│   │   ├── preprocess.py       # Data preprocessing
│   │   ├── scoring.py          # Deal scoring algorithm
│   │   └── stats.py            # Statistical analysis
│   ├── scraper/                # Web scrapers
│   │   ├── avito.py            # Avito scraper (Playwright)
│   │   ├── jumia.py            # Jumia scraper (Playwright)
│   │   ├── aliexpress.py       # AliExpress scraper (Playwright)
│   │   ├── dispatcher.py       # Scraper dispatcher
│   │   ├── exchange_rate.py    # Currency conversion
│   │   └── spiders/            # Scrapy spiders (Amazon, eBay)
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── manage.py
├── frontend/                   # React application
│   ├── src/
│   │   ├── api/                # API clients (auth, search, export, history)
│   │   ├── components/         # Reusable UI components
│   │   ├── context/            # React contexts (Auth, Toast)
│   │   ├── hooks/              # Custom React hooks
│   │   ├── pages/              # Page components
│   │   │   ├── SearchPage.jsx
│   │   │   ├── ResultsPage.jsx
│   │   │   ├── ItemPage.jsx
│   │   │   ├── HistoryPage.jsx
│   │   │   ├── AnalyticsPage.jsx
│   │   │   ├── ComparisonPage.jsx
│   │   │   ├── AlertsPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   └── RegisterPage.jsx
│   │   └── utils/              # Utilities and constants
│   ├── Dockerfile
│   └── package.json
├── docker/                     # Docker configuration
│   ├── docker-compose.yml      # Development compose
│   └── docker-compose.prod.yml # Production compose
├── deployment/                 # Production deployment configs
│   ├── gunicorn.conf.py
│   ├── nginx.conf
│   └── supervisor.conf
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── Makefile                    # Developer shortcuts
└── README.md
```

## Prerequisites

- **Python**: 3.11+
- **Node.js**: 20+
- **Docker** & **Docker Compose**
- **uv**: Python package and project manager

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/AmineAitLaamim/Market-Research-Pricing-Analysis.git
cd Market-Research-Pricing-Analysis
```

### 2. Environment Setup

Copy and configure environment files:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your configuration:
- Database credentials
- Redis URL
- Secret key
- API keys (if needed)

### 3. Running with Docker (Recommended)

Use the included `Makefile` to simplify Docker commands:

```bash
# Build and start all services
make build

# The stack includes:
# ├── db             (PostgreSQL 16)
# ├── redis          (Redis cache & broker)
# ├── backend        (Django + Gunicorn/Daphne)
# ├── celery-worker  (Celery background tasks)
# └── frontend       (Vite/Nginx serving React)
```

**Useful commands:**
```bash
make up          # Start services
make down        # Stop services
make logs        # View logs
make restart-frontend  # Restart frontend only
```

### 4. Running Locally (Development)

**Backend:**
```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 5. Testing

```bash
# Run all tests
make test

# Run with coverage
uv run --project backend pytest tests/ -v --cov=backend --cov-report=term-missing
```

### 6. Linting & Formatting

```bash
make lint

# Individual tools
cd backend
uv run flake8 .           # Linting
uv run black .            # Formatting
uv run isort .            # Import sorting
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login and get JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search/` | Start a new price search |
| GET | `/api/search/history/` | Get search history |
| GET | `/api/search/results/<id>/` | Get search results |

### Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/csv/<id>/` | Export results as CSV |
| GET | `/api/export/pdf/<id>/` | Export results as PDF |

## Data Mining Pipeline

The mining pipeline processes search results through multiple stages:

1. **Preprocessing**: Clean and normalize price data
2. **Statistical Analysis**: Calculate mean, median, std, quartiles
3. **Clustering**: Group products by price segments (K-Means, DBSCAN)
4. **Anomaly Detection**: Identify overpriced/underpriced items
5. **PCA**: Reduce dimensions for 2D visualization
6. **Association Rules**: Find product relationships
7. **Scoring**: Calculate deal scores for each product

## Production Deployment

For production deployment, use the production Docker Compose file:

```bash
docker compose -f docker/docker-compose.prod.yml up -d
```

The production stack includes:
- **Gunicorn** for WSGI HTTP server
- **Daphne** for ASGI/WebSocket
- **Nginx** as reverse proxy
- **Supervisor** for process management

Configuration files are available in the `deployment/` directory.

## License

This project is licensed under the MIT License.

## Contributors

- Amine Ait Laamim
