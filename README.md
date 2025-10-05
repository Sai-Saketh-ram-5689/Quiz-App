# Quiz App

A small Flask-based quiz application with teacher and student roles.

Features
- Teacher: create quizzes, add and edit questions for quizzes.
- Student: take quizzes with a client-side timer and server-side attempt tracking.
- One-attempt policy per quiz (results are recorded and visible on leaderboard).
- Semantic HTML5 + Bootstrap-based UI and small custom CSS in `static/css/style.css`.
- jQuery-based client-side form validation and UX helpers in `static/js/forms.js`.
- Simple SQLite database using Flask-SQLAlchemy. A lightweight helper ensures required columns exist if the schema is updated.

Prerequisites
- Python 3.8+ (recommended)
- Windows / PowerShell is supported (commands below are PowerShell examples)

Install
```powershell
python -m pip install -r requirements.txt
```

Environment
- The app reads configuration from environment variables with sensible defaults:
  - `SECRET_KEY` (fallback: a development secret inside app)
  - `DATABASE_URL` (fallback: `sqlite:///quiz.db` in the project root)

You can create a `.env` file in the project root with these values (optional):
```
SECRET_KEY=your-secret-here
DATABASE_URL=sqlite:///instance/quiz.db
```

Run (development server)
```powershell
python app.py
```
Open http://127.0.0.1:5000 in your browser.

Quick usage
1. Register as a teacher and create a quiz (specify duration in minutes).
2. Add questions to the quiz (teacher can also edit questions later).
3. Register as a student and take the quiz. A timer will show; submission is validated server-side and results saved.
4. View leaderboard for quiz scores.

Developer notes
- Database: the app uses SQLAlchemy models in `app.py`. On first run the app creates the database tables. A small helper runs at startup to add a `last_modified` column to the `quiz` table if it is missing (so existing databases are handled without manual migration).
- Attempt tracking: each student quiz access creates an `Attempt` record so the server can enforce timing and prevent multiple attempts.
- Templates: Jinja2 templates live in `templates/`. Static assets live in `static/` (CSS, JS).

Quick checks
- Syntax check:
```powershell
python -m py_compile app.py
```

Next steps (suggestions)
- Add question delete functionality with confirmation.
- Introduce Alembic for robust, versioned DB migrations.
- Add unit tests for grading and attempt timing.

If you want any of these implemented, tell me which one and I will add it next.
