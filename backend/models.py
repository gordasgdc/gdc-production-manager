"""
GDC Production Manager - Database models
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Video-production specific status pipeline. Order matters (it's a real
# sequence a project moves through), used both for validation and for the
# dashboard's pipeline visualization.
PROJECT_STATUSES = [
    "planning",
    "filming",
    "editing",
    "coloring",
    "review",
    "final",
    "delivered",
]

PROJECT_TYPES = [
    "film",
    "commercial",
    "wedding",
    "documentary",
    "broadcast",
    "music_video",
    "corporate",
    "other",
]

PAYMENT_STATUSES = ["unpaid", "partial", "paid"]


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(120), nullable=True)
    language = db.Column(db.String(5), nullable=False, default="ro")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    clients = db.relationship(
        "Client", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    projects = db.relationship(
        "Project", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    templates = db.relationship(
        "WorkflowTemplate", backref="owner", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "language": self.language,
        }


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship("Project", backref="client", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "company": self.company,
            "email": self.email,
            "phone": self.phone,
            "notes": self.notes,
            "project_count": len(self.projects),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class WorkflowTemplate(db.Model):
    """A named, reusable checklist of stages for a given kind of shoot."""

    __tablename__ = "workflow_templates"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    project_type = db.Column(db.String(30), nullable=True)
    stages = db.Column(db.Text, nullable=True)  # comma-separated custom stage notes

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "project_type": self.project_type,
            "stages": self.stages.split(",") if self.stages else [],
        }


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=True)
    template_id = db.Column(
        db.Integer, db.ForeignKey("workflow_templates.id"), nullable=True
    )

    title = db.Column(db.String(200), nullable=False)
    project_type = db.Column(db.String(30), nullable=False, default="other")
    status = db.Column(db.String(30), nullable=False, default="planning")

    shoot_location = db.Column(db.String(300), nullable=True)
    shoot_date = db.Column(db.Date, nullable=True)
    delivery_date = db.Column(db.Date, nullable=True)

    path_raw = db.Column(db.String(500), nullable=True)
    path_edit = db.Column(db.String(500), nullable=True)
    path_export = db.Column(db.String(500), nullable=True)

    budget_total = db.Column(db.Float, nullable=True, default=0)
    amount_paid = db.Column(db.Float, nullable=True, default=0)
    payment_status = db.Column(db.String(20), nullable=False, default="unpaid")

    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "project_type": self.project_type,
            "status": self.status,
            "client_id": self.client_id,
            "client_name": self.client.name if self.client else None,
            "template_id": self.template_id,
            "shoot_location": self.shoot_location,
            "shoot_date": self.shoot_date.isoformat() if self.shoot_date else None,
            "delivery_date": self.delivery_date.isoformat()
            if self.delivery_date
            else None,
            "path_raw": self.path_raw,
            "path_edit": self.path_edit,
            "path_export": self.path_export,
            "budget_total": self.budget_total,
            "amount_paid": self.amount_paid,
            "payment_status": self.payment_status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
