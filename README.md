# NagarDrishti — Connected Project

## Frontend
Upload the contents of `frontend/` to your GitHub Pages repository. The main page is `index.html`.

Before using the report/login pages, edit `frontend/config.js`:
`const API_BASE = "https://YOUR-BACKEND-DOMAIN.example.com/api";`

## Backend
Deploy the `backend/` folder on a Python/Flask hosting service.

Set environment variables:
- `DEPT_USER` = department login username
- `DEPT_PASSWORD_HASH` = Werkzeug password hash
- `FRONTEND_ORIGIN` = your GitHub Pages origin, e.g. `https://yourname.github.io`

Do NOT publish a real department password in GitHub.

## Flow
Citizen -> report.html -> Flask API -> SQLite -> Department Login -> Dashboard -> status update.

GitHub Pages cannot run Python. The backend must be deployed separately.
