import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import (
    User, Course, Lesson, Assignment, Quiz, Enrollment, Submission,
    QuizAttempt, Subscription, Activity, SCHEMAS
)

app = FastAPI(title="EduSaaS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "EduSaaS backend running"}

@app.get("/schema")
def get_schema():
    return {"collections": SCHEMAS}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Basic endpoints for key flows (create + list)

class CreateCourseRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    teacher_id: str
    category: Optional[str] = None
    tags: List[str] = []
    thumbnail_url: Optional[str] = None
    level: str = "beginner"

@app.post("/courses")
def create_course(payload: CreateCourseRequest):
    course = Course(
        title=payload.title,
        description=payload.description,
        teacher_id=payload.teacher_id,
        category=payload.category,
        tags=payload.tags,
        thumbnail_url=payload.thumbnail_url,
        level=payload.level,
        is_published=False,
    )
    course_id = create_document("course", course)
    return {"id": course_id, "message": "Course created"}

@app.get("/courses")
def list_courses():
    items = get_documents("course")
    return {"items": items}

class CreateLessonRequest(BaseModel):
    course_id: str
    title: str
    video_url: Optional[str] = None
    content: Optional[str] = None
    order: int = 0

@app.post("/lessons")
def create_lesson(payload: CreateLessonRequest):
    lesson = Lesson(**payload.model_dump())
    lesson_id = create_document("lesson", lesson)
    return {"id": lesson_id, "message": "Lesson created"}

@app.get("/lessons")
def list_lessons(course_id: Optional[str] = None):
    filter_q = {"course_id": course_id} if course_id else {}
    items = get_documents("lesson", filter_q)
    return {"items": items}

class CreateAssignmentRequest(BaseModel):
    course_id: str
    title: str
    instructions: str

@app.post("/assignments")
def create_assignment(payload: CreateAssignmentRequest):
    assignment = Assignment(
        course_id=payload.course_id,
        title=payload.title,
        instructions=payload.instructions,
    )
    assignment_id = create_document("assignment", assignment)
    return {"id": assignment_id, "message": "Assignment created"}

@app.get("/assignments")
def list_assignments(course_id: Optional[str] = None):
    filter_q = {"course_id": course_id} if course_id else {}
    items = get_documents("assignment", filter_q)
    return {"items": items}

class CreateQuizRequest(BaseModel):
    course_id: str
    title: str

@app.post("/quizzes")
def create_quiz(payload: CreateQuizRequest):
    quiz = Quiz(course_id=payload.course_id, title=payload.title, questions=[])
    quiz_id = create_document("quiz", quiz)
    return {"id": quiz_id, "message": "Quiz created"}

@app.get("/quizzes")
def list_quizzes(course_id: Optional[str] = None):
    filter_q = {"course_id": course_id} if course_id else {}
    items = get_documents("quiz", filter_q)
    return {"items": items}

class EnrollRequest(BaseModel):
    course_id: str
    student_id: str

@app.post("/enroll")
def enroll_student(payload: EnrollRequest):
    enr = create_document("enrollment", {
        "course_id": payload.course_id,
        "student_id": payload.student_id,
        "status": "active",
        "progress_percent": 0.0,
    })
    return {"id": enr, "message": "Enrollment created"}

@app.get("/enrollments")
def list_enrollments(course_id: Optional[str] = None, student_id: Optional[str] = None):
    q: Dict[str, Any] = {}
    if course_id:
        q["course_id"] = course_id
    if student_id:
        q["student_id"] = student_id
    items = get_documents("enrollment", q)
    return {"items": items}

class SubmitAssignmentRequest(BaseModel):
    assignment_id: str
    student_id: str
    content_url: Optional[str] = None
    content_text: Optional[str] = None

@app.post("/submit")
def submit_assignment(payload: SubmitAssignmentRequest):
    sub = Submission(**payload.model_dump())
    sub_id = create_document("submission", sub)
    return {"id": sub_id, "message": "Submission received"}

@app.get("/submissions")
def list_submissions(assignment_id: Optional[str] = None, student_id: Optional[str] = None):
    q: Dict[str, Any] = {}
    if assignment_id:
        q["assignment_id"] = assignment_id
    if student_id:
        q["student_id"] = student_id
    items = get_documents("submission", q)
    return {"items": items}

class TrackActivityRequest(BaseModel):
    user_id: str
    action: str
    resource_type: str
    resource_id: str

@app.post("/activity")
def track_activity(payload: TrackActivityRequest):
    act = Activity(
        user_id=payload.user_id,
        action=payload.action,
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
        metadata={}
    )
    act_id = create_document("activity", act)
    return {"id": act_id, "message": "Activity tracked"}

# Subscription mock endpoints (no payment provider integration here)
class CreateSubscriptionRequest(BaseModel):
    user_id: str
    plan: str = "free"

@app.post("/subscriptions")
def create_subscription(payload: CreateSubscriptionRequest):
    sub = Subscription(user_id=payload.user_id, plan=payload.plan)
    sub_id = create_document("subscription", sub)
    return {"id": sub_id, "message": "Subscription created"}

@app.get("/subscriptions")
def list_subscriptions(user_id: Optional[str] = None):
    q = {"user_id": user_id} if user_id else {}
    items = get_documents("subscription", q)
    return {"items": items}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
