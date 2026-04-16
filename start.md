# Quick Start Guide

Welcome to the Result Analysis Dashboard! Follow these simple instructions to set up and run this project locally on your machine after cloning it from GitHub.

## Prerequisites
- **Python 3.8+** installed on your system.
- **MySQL Server** installed and running locally.

## 1. Database Configuration
This application relies on a MySQL database to serve results. You must create the `result_dashboard` database and its corresponding tables before running the app.

1. Open MySQL Command Line or MySQL Workbench.
2. Run the following SQL setup script:

```sql
CREATE DATABASE IF NOT EXISTS result_dashboard;
USE result_dashboard;

-- Admin Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Students Table
CREATE TABLE students (
    student_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150),
    password VARCHAR(255),
    cpp INT,
    java INT,
    aptitude INT,
    dsa INT
);

-- Insert a default admin for testing purposes
INSERT INTO users (username, password) VALUES ('admin', 'admin123');
```

**⚠️ Important:** The application logic in `main.py` explicitly connects using the following database variables inside `get_db_connection()`:
- **Host:** `localhost`
- **User:** `root`
- **Password:** `Paarthkumar@986892`
*(You will need to edit this password string in `main.py` on line 17 to match your personal MySQL database password.)*

## 2. Install Dependencies

1. Open your terminal at the root of your cloned project folder.
2. Create and activate a Python virtual environment:
   
   **Windows:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
   **Mac/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required python packages from your `requirements.txt`:
   ```powershell
   pip install -r requirements.txt
   ```
   *(Core dependencies include: `fastapi`, `uvicorn`, `mysql-connector-python`, `jinja2`, and `python-multipart`)*

## 3. Run the Application

Once the database handles are set up and your virtual environment is active, start the FastAPI server with auto-reload:

```powershell
uvicorn main:app --reload
```

## 4. Access the Dashboard

- Open your web browser and navigate down to the local host address: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.
- Choose between **Student Portal** or **Admin Portal** to login and explore!
