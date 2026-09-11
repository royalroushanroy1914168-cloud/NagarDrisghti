# NagarDrishti

AI-powered civic problem mapping prototype for the Design for Bharat project.

## Features

- Civic problem photo upload
- Backend image analysis endpoint
- GPS capture in browser
- Civic Priority Score
- SQLite report storage
- Report history
- Interactive OpenStreetMap/Leaflet map
- Report status API
- Responsive frontend

## Project structure

```text
NagarDrishti/
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── ai_detector.py
│   ├── priority.py
│   ├── requirements.txt
│   └── uploads/
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

## Run backend

Open a terminal in `backend`:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Backend:
`http://127.0.0.1:5000`

## Run frontend

Open `frontend/index.html` with VS Code Live Server.

The frontend expects the backend at:

`http://127.0.0.1:5000/api`

## Important

The current `ai_detector.py` is a prototype detector. It validates the uploaded image and returns a demo pothole result. Replace it with a trained computer-vision model for genuine AI detection.

The map uses Leaflet and OpenStreetMap tiles, so internet access is needed for the map.
