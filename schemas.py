"""
Database Schemas for EduSaaS

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase of the class name.
Examples:
- User -> "user"
- Course -> "course"

These models are also returned via GET /schema for tooling and validation.
"""
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Core identities
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    role: Literal["teacher", "student", "admin"] = Field("student", description="Role in the platform")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    is_active: bool = Field(True, description="Whether user is active")

class Course(BaseModel):
    title: str = Field(..., description="Course title")
    description: Optional[str] = Field("", description="Short description")
    teacher_id: str = Field(..., description="Owner teacher user id")
    category: Optional[str] = Field(None, description="Category or topic")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    level: Literal["beginner", "intermediate", "advanced"] = Field("beginner")
    is_published: bool = Field(False)

class Lesson(BaseModel):
    course_id: str
    title: str
    video_url: Optional[str] = None
    content: Optional[str] = None
    order: int = 0
    duration_minutes: Optional[int] = None

class Assignment(BaseModel):
    course_id: str
    title: str
    instructions: str
    due_date: Optional[datetime] = None
    max_points: int = 100

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int

class Quiz(BaseModel):
    course_id: str
    title: str
    questions: List[QuizQuestion] = Field(default_factory=list)
    time_limit_minutes: Optional[int] = None

class Enrollment(BaseModel):
    course_id: str
    student_id: str
    status: Literal["active", "completed", "dropped"] = "active"
    progress_percent: float = 0.0

class Submission(BaseModel):
    assignment_id: str
    student_id: str
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    grade: Optional[float] = None
    feedback: Optional[str] = None

class QuizAttempt(BaseModel):
    quiz_id: str
    student_id: str
    answers: List[int]
    score: Optional[float] = None

class Subscription(BaseModel):
    user_id: str
    plan: Literal["free", "pro", "team", "enterprise"] = "free"
    status: Literal["active", "past_due", "canceled"] = "active"
    renews_at: Optional[datetime] = None

class Activity(BaseModel):
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Helper to expose schema metadata for tooling
class SchemaInfo(BaseModel):
    collections: Dict[str, Dict[str, Any]]

SCHEMAS: Dict[str, Any] = {
    "user": User.model_json_schema(),
    "course": Course.model_json_schema(),
    "lesson": Lesson.model_json_schema(),
    "assignment": Assignment.model_json_schema(),
    "quiz": Quiz.model_json_schema(),
    "enrollment": Enrollment.model_json_schema(),
    "submission": Submission.model_json_schema(),
    "quizattempt": QuizAttempt.model_json_schema(),
    "subscription": Subscription.model_json_schema(),
    "activity": Activity.model_json_schema(),
}
