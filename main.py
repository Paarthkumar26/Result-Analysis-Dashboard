import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector

load_dotenv(Path(__file__).resolve().parent / ".env")

app = FastAPI()

_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")
templates = Jinja2Templates(directory="templates")


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "result_dashboard"),
    )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/student-login", response_class=HTMLResponse)
def student_login_page(request: Request):
    return templates.TemplateResponse("student_login.html", {"request": request})


@app.post("/student-login", response_class=HTMLResponse)
def student_login(
    request: Request,
    student_id: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM students WHERE student_id = %s AND password = %s"
    cursor.execute(query, (student_id, password))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

    if student:
        return RedirectResponse(url=f"/student-dashboard/{student_id}", status_code=303)

    return templates.TemplateResponse(
        "student_login.html",
        {
            "request": request,
            "error": "Invalid Student ID or Password"
        }
    )


@app.get("/admin-login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/admin-login", response_class=HTMLResponse)
def admin_login(
    request: Request,
    admin_id: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (admin_id, password))
    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    if admin:
        return RedirectResponse(url="/admin-dashboard", status_code=303)

    return templates.TemplateResponse(
        "admin_login.html",
        {
            "request": request,
            "error": "Invalid Admin ID or Password"
        }
    )


@app.get("/student-dashboard/{student_id}", response_class=HTMLResponse)
def student_dashboard(request: Request, student_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM students WHERE student_id = %s"
    cursor.execute(query, (student_id,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

    if not student:
        return HTMLResponse(content="<h1>Student not found</h1>", status_code=404)

    # Calculate required properties for the template
    cpp = student['cpp']
    java = student['java']
    apt = student['aptitude']
    dsa = student['dsa']

    def get_status(marks):
        if marks >= 80: return "Strong"
        elif marks >= 50: return "Average"
        else: return "Weak"

    student['cpp_status'] = get_status(cpp)
    student['java_status'] = get_status(java)
    student['aptitude_status'] = get_status(apt)
    student['dsa_status'] = get_status(dsa)

    total = cpp + java + apt + dsa
    percentage = total / 4.0
    student['overall_percentage'] = round(percentage, 2)

    subjects = {'C++': cpp, 'Java': java, 'Aptitude': apt, 'DSA': dsa}
    student['best_subject'] = max(subjects, key=subjects.get)
    student['weak_subject'] = min(subjects, key=subjects.get)
    
    suggestions = []
    if student['weak_subject'] == 'C++':
        suggestions.append("Focus on pointers and OOP concepts in C++.")
    elif student['weak_subject'] == 'Java':
        suggestions.append("Practice multithreading and collection framework in Java.")
    elif student['weak_subject'] == 'Aptitude':
        suggestions.append("Practice time management and problem solving for Aptitude.")
    elif student['weak_subject'] == 'DSA':
        suggestions.append("Work on your fundamental data structures and algorithms.")

    if percentage >= 80:
        suggestions.append("Great overall performance! Keep up the good work.")
    elif percentage >= 50:
        suggestions.append("You are doing okay, but there is room for improvement.")
    else:
        suggestions.append("You need significant improvement. Please consult your instructors.")
        
    student['suggestions'] = suggestions

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": student
        }
    )


@app.get("/admin-dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()

    if not students:
        data = {
            "total_students": 0,
            "avg_score": 0,
            "top_student": "None",
            "leaderboard": [],
            "cpp_avg": 0,
            "java_avg": 0,
            "aptitude_avg": 0,
            "dsa_avg": 0,
        }
    else:
        total_students = len(students)
        cpp_total = sum(s['cpp'] for s in students)
        java_total = sum(s['java'] for s in students)
        apt_total = sum(s['aptitude'] for s in students)
        dsa_total = sum(s['dsa'] for s in students)
        
        cpp_avg = round(cpp_total / total_students, 2)
        java_avg = round(java_total / total_students, 2)
        apt_avg = round(apt_total / total_students, 2)
        dsa_avg = round(dsa_total / total_students, 2)
        
        avg_score = round((cpp_avg + java_avg + apt_avg + dsa_avg) / 4, 2)
        
        calculated_students = []
        for s in students:
            avg_marks = round((s['cpp'] + s['java'] + s['aptitude'] + s['dsa']) / 4, 2)
            calculated_students.append((s['student_id'], s['name'], avg_marks))
        
        calculated_students.sort(key=lambda x: x[2], reverse=True)
        top_student = calculated_students[0][1] if calculated_students else "None"
        
        leaderboard = calculated_students[:10]
        
        data = {
            "total_students": total_students,
            "avg_score": avg_score,
            "top_student": top_student,
            "leaderboard": leaderboard,
            "cpp_avg": cpp_avg,
            "java_avg": java_avg,
            "aptitude_avg": apt_avg,
            "dsa_avg": dsa_avg
        }

    return templates.TemplateResponse(
        "admin_dashboard.html", 
        {
            "request": request,
            "data": data
        }
    )


@app.get("/logout")
def logout():
    # If using FastAPI, a simple redirect clears the view.
    # Note: Because this app does not use session cookies yet,
    # visiting this URL just brings you back to the main menu.
    return RedirectResponse(url="/", status_code=303)


@app.get("/admin/edit/{student_id}", response_class=HTMLResponse)
def edit_student_page(request: Request, student_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

    if not student:
        return HTMLResponse(content="<h1>Student not found</h1>", status_code=404)

    return templates.TemplateResponse(
        "edit_student.html",
        {
            "request": request,
            "student": student
        }
    )


@app.post("/admin/update/{student_id}")
def update_student(
    student_id: str,
    name: str = Form(...),
    password: str = Form(...),
    cpp: int = Form(...),
    java: int = Form(...),
    aptitude: int = Form(...),
    dsa: int = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        UPDATE students 
        SET name = %s, password = %s, cpp = %s, java = %s, aptitude = %s, dsa = %s 
        WHERE student_id = %s
    """
    cursor.execute(query, (name, password, cpp, java, aptitude, dsa, student_id))
    conn.commit()

    cursor.close()
    conn.close()

    return RedirectResponse(url="/admin-dashboard", status_code=303)


@app.get("/admin/delete/{student_id}")
def delete_student(student_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return RedirectResponse(url="/admin-dashboard", status_code=303)
