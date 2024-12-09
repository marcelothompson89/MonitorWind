# Monitor Wind

A web application that monitors and displays information from various sources including news, projects, and laws. The application includes web scraping capabilities to gather information from different websites and presents it in a unified interface.

## Features

- Web scraping from multiple sources
- Information storage in SQLite database
- Modern React frontend with filtering capabilities
- FastAPI backend with REST API
- Real-time search functionality
- Country-based filtering
- Date range filtering

## Setup

### Backend

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend:
```bash
cd backend
uvicorn main:app --reload
```

### Frontend

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Run the frontend development server:
```bash
npm run dev
```

## Project Structure

```
MonitorWind/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── scrapers/
│   │   └── api/
│   ├── main.py
│   └── database.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
├── requirements.txt
└── README.md
```
