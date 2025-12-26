# RumorLens

Weibo Rumor Detection Platform powered by DeepSeek AI.

## Features

- Single and batch rumor detection
- Credibility scoring and risk level assessment
- Detailed analysis with keywords, sentiment, and category classification
- Detection history management
- Analytics dashboard with trend visualization
- User authentication system

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- DeepSeek API

### Frontend
- Vue 3
- Vite
- Ant Design Vue
- Pinia
- ECharts

### UI Design
- Minimalism & Swiss Style
- Instrument Sans + Newsreader fonts
- 12-column grid system

## Quick Start

### Prerequisites
- Docker & Docker Compose
- DeepSeek API Key

### Setup

1. Clone the repository:
```bash
cd RumorLens
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Add your DeepSeek API key to `.env`:
```
DEEPSEEK_API_KEY=your-api-key-here
```

4. Start the services:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1/docs

### Development Setup (without Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Project Structure

```
RumorLens/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Configuration
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   └── data/            # Datasets
├── frontend/            # Vue 3 frontend
│   └── src/
│       ├── api/         # API calls
│       ├── components/  # Vue components
│       ├── stores/      # Pinia stores
│       └── views/       # Page views
└── docker-compose.yml
```

## Dataset

This project uses the Ma-Weibo dataset:
- 4664 labeled events (2313 rumors, 2351 non-rumors)
- Source: https://www.scidb.cn/en/detail?dataSetId=1085347f720f4cfc97a157e469734a66

## License

MIT
