# 🧠 Quiz App  

A full-featured **Flask-based Quiz Application** built for both teachers and students.  
It allows teachers to create quizzes and manage questions, while students can take quizzes with a timer, view scores, and check leaderboards.

---

## ✨ Features
- 👨‍🏫 **Teacher Mode**
  - Create quizzes with duration.
  - Add, edit, and manage questions.
  - View leaderboard for student scores.
- 🧑‍🎓 **Student Mode**
  - Register, log in, and take quizzes.
  - One-attempt per quiz (tracked in the database).
  - View leaderboard after submission.
- 🧩 **Core Highlights**
  - Responsive UI with **Bootstrap + minimal CSS**.
  - jQuery-based **form validation** & timers.
  - Lightweight **SQLite** database using Flask-SQLAlchemy.
  - Clean structure: `/templates` for HTML, `/static` for CSS/JS.

---

## 🖼️ Screenshots

### 🏠 Homepage
![Homepage](screenshots/homepage.png)

### 🧾 Register Page
![Register](screenshots/register.png)

### 🔐 Login Page
![Login](screenshots/login.png)

### 🧮 Dashboard (Student View)
![Dashboard](screenshots/dashboard_student.png)

### 🧑‍🏫 Dashboard (Teacher View)
![Dashboard Teacher](screenshots/dashboard_teacher.png)

### 🕒 Quiz Page (With Timer)
![Quiz Page](screenshots/quiz_page.png)

### 🏆 Leaderboard
![Leaderboard](screenshots/leaderboard.png)

---

## ⚙️ Prerequisites
- **Python 3.8+**
- Works on **Windows / Linux / macOS**

---

## 🧩 Installation

Clone the repository:
```bash
git clone https://github.com/Sai-Saketh-ram-5689/Quiz-App.git
cd Quiz-App
