import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables from a .env file if present
load_dotenv()

app = Flask(__name__)
# Use environment variables when available (non-negotiable requirement)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_very_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///quiz.db')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# =============================
# MODELS
# =============================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "teacher" or "student"

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    duration = db.Column(db.Integer, default=10)  # minutes
    creator = db.relationship('User', backref='quizzes')
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    question_text = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(100))
    option_b = db.Column(db.String(100))
    option_c = db.Column(db.String(100))
    option_d = db.Column(db.String(100))
    correct_answer = db.Column(db.String(1))  # 'A','B','C','D'

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref='results')
    quiz = db.relationship('Quiz', backref='results')


class Attempt(db.Model):
    """Tracks a user's attempt at a quiz for server-side timer enforcement and single-attempt logic."""
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completed_time = db.Column(db.DateTime)
    quiz = db.relationship('Quiz', backref='attempts')
    user = db.relationship('User', backref='attempts')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =============================
# ROUTES
# =============================
@app.route('/')
def index():
    return render_template('index.html')


# ---------- AUTH ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password_raw = request.form['password']
        role = request.form['role']

        # Basic server-side validation
        if not username or not password_raw or role not in ('student', 'teacher'):
            flash('Please provide a username, password and select a valid role.', 'warning')
            return redirect(url_for('register'))

        if len(password_raw) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return redirect(url_for('register'))

        password = generate_password_hash(password_raw)
        # Prevent duplicate usernames gracefully
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password, role=role)
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Registration failed; username may already exist.', 'danger')
            return redirect(url_for('register'))

        flash('Registered successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ---------- DASHBOARD ----------
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        quizzes = Quiz.query.filter_by(created_by=current_user.id).all()
    else:
        quizzes = Quiz.query.all()
    return render_template('dashboard.html', quizzes=quizzes)


# ---------- CREATE QUIZ (Teacher) ----------
@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if current_user.role != 'teacher':
        flash("Only teachers can create quizzes.", 'warning')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        duration = int(request.form['duration'])
        quiz = Quiz(title=title, created_by=current_user.id, duration=duration)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created! Now add questions.', 'success')
        return redirect(url_for('add_question', quiz_id=quiz.id))

    return render_template('create_quiz.html')


@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if current_user.id != quiz.created_by:
        flash("You are not authorized to edit this quiz.", 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Check if the user wants to finish adding questions
        if 'finish' in request.form:
            return redirect(url_for('dashboard'))
            
        q = Question(
            quiz_id=quiz_id,
            question_text=request.form['question'],
            option_a=request.form['option_a'],
            option_b=request.form['option_b'],
            option_c=request.form['option_c'],
            option_d=request.form['option_d'],
            correct_answer=request.form['correct']
        )
        db.session.add(q)
        db.session.commit()
        # Update quiz last_modified so students get the new questions
        quiz.last_modified = datetime.datetime.utcnow()
        db.session.commit()
        flash('Question added!', 'success')
    # Retrieve existing questions for display to the teacher
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.id).all()
    return render_template('add_question.html', quiz=quiz, questions=questions)


@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    q = Question.query.get_or_404(question_id)
    quiz = Quiz.query.get(q.quiz_id)
    # Only the quiz creator (teacher) may edit
    if current_user.id != quiz.created_by:
        flash("You are not authorized to edit this question.", 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Basic validation
        question_text = request.form.get('question', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct = request.form.get('correct')

        if not question_text or not option_a or not option_b or not option_c or not option_d or correct not in ('A','B','C','D'):
            flash('All fields are required and a valid correct answer must be selected.', 'warning')
            return render_template('edit_question.html', question=q, quiz=quiz)

        q.question_text = question_text
        q.option_a = option_a
        q.option_b = option_b
        q.option_c = option_c
        q.option_d = option_d
        q.correct_answer = correct
        # mark quiz as modified so in-progress attempts are aware
        quiz.last_modified = datetime.datetime.utcnow()
        db.session.commit()
        flash('Question updated successfully.', 'success')
        return redirect(url_for('add_question', quiz_id=quiz.id))

    return render_template('edit_question.html', question=q, quiz=quiz)


# ---------- TAKE QUIZ (Student) ----------
@app.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # Prevent multiple attempts: if a Result already exists for this user & quiz, block further attempts
    existing_result = Result.query.filter_by(quiz_id=quiz.id, user_id=current_user.id).first()
    if existing_result:
        flash('You have already attempted this quiz. You can view the leaderboard.', 'info')
        return redirect(url_for('leaderboard', quiz_id=quiz.id))

    if request.method == 'POST':
        # Re-query questions to ensure grading uses the latest set
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        # POST should contain attempt_id so we can validate timing
        attempt_id = request.form.get('attempt_id')
        attempt = None
        if attempt_id:
            attempt = Attempt.query.get(int(attempt_id))

        now = datetime.datetime.utcnow()
        # If attempt isn't found or doesn't belong to this user, reject
        if not attempt or attempt.user_id != current_user.id or attempt.quiz_id != quiz.id:
            flash('Invalid or expired attempt. Please try opening the quiz again.', 'danger')
            return redirect(url_for('dashboard'))

        elapsed = (now - attempt.start_time).total_seconds()
        allowed = quiz.duration * 60
        if elapsed > allowed:
            # Time expired: mark attempt completed and record zero or partial as desired
            attempt.completed = True
            attempt.completed_time = now
            db.session.commit()
            # Create a Result with score 0 due to timeout
            result = Result(quiz_id=quiz.id, user_id=current_user.id, score=0)
            db.session.add(result)
            db.session.commit()
            flash('Time expired. Your attempt was recorded as timed-out and scored 0.', 'warning')
            return redirect(url_for('leaderboard', quiz_id=quiz.id))

        # Within allowed time: grade
        score = 0
        for q in questions:
            answer = request.form.get(str(q.id))
            if answer == q.correct_answer:
                score += 1

        result = Result(quiz_id=quiz.id, user_id=current_user.id, score=score)
        db.session.add(result)
        # mark attempt completed
        attempt.completed = True
        attempt.completed_time = now
        db.session.commit()
        flash(f"Quiz submitted! You scored {score}/{len(questions)}", 'info')
        return redirect(url_for('leaderboard', quiz_id=quiz.id))

    # GET: create or reuse an active attempt
    attempt = Attempt.query.filter_by(quiz_id=quiz.id, user_id=current_user.id, completed=False).first()
    if attempt:
        # If the quiz was modified after the attempt started, expire the old attempt and create a new one
        if quiz.last_modified and quiz.last_modified > attempt.start_time:
            attempt.completed = True
            attempt.completed_time = datetime.datetime.utcnow()
            db.session.commit()
            attempt = None

    if not attempt:
        attempt = Attempt(quiz_id=quiz.id, user_id=current_user.id)
        db.session.add(attempt)
        db.session.commit()
    # After ensuring the attempt is current, fetch the latest questions for the student view
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    return render_template('take_quiz.html', quiz=quiz, questions=questions, attempt=attempt)


# ---------- LEADERBOARD ----------
@app.route('/leaderboard/<int:quiz_id>')
@login_required
def leaderboard(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # Perform a join to get user information along with results
    results = db.session.query(Result, User).join(User).filter(Result.quiz_id == quiz_id).order_by(Result.score.desc()).all()
    return render_template('leaderboard.html', results=results, quiz=quiz)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Ensure DB schema has the latest columns (helps when adding columns without migrations)
        def ensure_db_columns():
            try:
                # Get columns of quiz table
                rows = db.session.execute(text("PRAGMA table_info('quiz')")).fetchall()
                cols = [r[1] for r in rows]
                if 'last_modified' not in cols:
                    # Add the column; SQLite supports ADD COLUMN for simple cases
                    db.session.execute(text("ALTER TABLE quiz ADD COLUMN last_modified DATETIME"))
                    # Initialize existing rows to current UTC
                    now = datetime.datetime.utcnow().isoformat()
                    db.session.execute(text("UPDATE quiz SET last_modified = :now"), {'now': now})
                    db.session.commit()
                    print('Added last_modified column to quiz table and initialized values.')
            except Exception as e:
                # Log but don't crash startup for safety
                print('ensure_db_columns error:', e)

        ensure_db_columns()
    app.run(debug=True)
else:
    # When the module is imported (e.g., by the reloader), make sure the helper is available
    def ensure_db_columns():
        try:
            rows = db.session.execute(text("PRAGMA table_info('quiz')")).fetchall()
            cols = [r[1] for r in rows]
            if 'last_modified' not in cols:
                db.session.execute(text("ALTER TABLE quiz ADD COLUMN last_modified DATETIME"))
                now = datetime.datetime.utcnow().isoformat()
                db.session.execute(text("UPDATE quiz SET last_modified = :now"), {'now': now})
                db.session.commit()
                print('Added last_modified column to quiz table and initialized values.')
        except Exception as e:
            print('ensure_db_columns error:', e)


# Also ensure the DB schema once per process before handling requests (handles the reloader)
_db_columns_checked = False

@app.before_request
def _ensure_columns_before_request():
    global _db_columns_checked
    if not _db_columns_checked:
        try:
            ensure_db_columns()
        except Exception as e:
            print('ensure_db_columns error in before_request:', e)
        _db_columns_checked = True