## 🖥 Backend Overview

The backend of the **Course Management System (Mini LMS)** is built using **Django** and **Django REST Framework (DRF)**. It provides a secure and scalable RESTful API to manage authentication, courses, lessons, enrollments, and student progress tracking.

The system follows a **role-based architecture** where users are categorized as:

- **Student**
- **Instructor**

Each role has specific permissions and access controls.

---

## 🔐 Authentication System

Authentication is implemented using **JWT (JSON Web Tokens)** with SimpleJWT.

### Features:
- User registration
- User login
- Access & refresh tokens
- Protected API routes
- Role-based permissions

Only authenticated users can access protected endpoints.

---

## 📚 Course Management

Instructors can:

- Create courses
- Update their own courses
- Delete their own courses
- Upload course thumbnail

All users can:

- View course list (with pagination)
- View course details

Each course is linked to an instructor using a foreign key relationship.

---

## 🎬 Lesson Management

Each course contains multiple lessons.

Instructors can:

- Add lessons
- Update lessons
- Delete lessons
- Control lesson order

Each lesson includes:
- Title
- Video URL (YouTube/Vimeo)
- Duration (in minutes)
- Order/position

Lessons are returned in ordered format.

---

## 📝 Enrollment System

Students can:

- Enroll in courses
- Prevent duplicate enrollment
- View enrolled courses
- Store enrollment date

A unique constraint ensures that a student cannot enroll in the same course twice.

---

## 📊 Progress Tracking

Students can:

- Mark lessons as completed
- View completed lesson count
- See progress percentage per course

Progress is calculated dynamically based on completed lessons.

---

## 🛠 API Architecture

The backend follows RESTful principles:

- Proper HTTP methods (GET, POST, PUT, DELETE)
- Serializer validation
- Role-based permission classes
- Pagination support
- Clean model relationships
- Proper error handling

All responses are served in JSON format and designed to integrate with a React frontend.

---

## 🔒 Security & Best Practices

- JWT Authentication
- Role-based access control
- Protected routes
- Proper validation
- Clean database relationships
- Production-ready configuration support