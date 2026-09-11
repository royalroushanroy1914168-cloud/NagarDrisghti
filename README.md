# NagarDrishti Department Login
Citizens submit reports without login. Only authenticated department accounts can view all submitted details and update status.

## Local setup
cd backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt

Windows CMD:
set DEPT_USERNAME=municipal
set DEPT_PASSWORD=CHANGE_TO_A_STRONG_PASSWORD
set NAGAR_SECRET_KEY=CHANGE_TO_A_LONG_RANDOM_SECRET
set FRONTEND_ORIGIN=http://127.0.0.1:5500
python app.py

Open frontend/department-login.html with Live Server.

Do not put passwords in HTML/JavaScript or publish them in GitHub. For online use, deploy the Flask backend over HTTPS and set FRONTEND_ORIGIN to your GitHub Pages URL.
