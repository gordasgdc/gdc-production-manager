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

COURSE_STATUSES = ["scheduled", "confirmed", "completed", "cancelled"]
COURSE_LOCATIONS = ["online", "in_person"]

PRODUCT_TYPES = ["dctl", "powergrade", "lut", "preset", "template", "other"]

CURRENCIES = ["EUR", "RON"]

CHECKLIST_TYPES = ["pre_filming", "post_filming", "general"]
REMINDER_TYPES = ["deadline", "invoice", "meeting", "general"]

EQUIPMENT_STATUSES = ["available", "checked_out", "maintenance", "lost"]


def _worst_payment_status(projects):
    """Rolls up a list of projects into one badge-worthy status - the most
    urgent one wins, so a client/company with even ONE unpaid project shows
    red, not a falsely-reassuring average. None means "no projects yet",
    which callers render as no badge at all rather than a false "paid"."""
    statuses = {p.payment_status for p in projects if p.payment_status}
    if "unpaid" in statuses:
        return "unpaid"
    if "partial" in statuses:
        return "partial"
    if "paid" in statuses:
        return "paid"
    return None


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    # Cod de recuperare afisat o SINGURA DATA la inregistrare (si rotit la
    # fiecare reset reusit) - singura cale de a recupera accesul daca
    # userul uita parola, fiindca aplicatia e 100% offline, fara email.
    recovery_code_hash = db.Column(db.String(255), nullable=True)
    display_name = db.Column(db.String(120), nullable=True)
    language = db.Column(db.String(5), nullable=False, default="ro")
    theme = db.Column(db.String(10), nullable=False, default="dark")
    currency = db.Column(db.String(3), nullable=False, default="EUR")

    # Optional self-hosted sync: point this instance at another running
    # GDC Production Manager instance to push/pull a full data snapshot.
    sync_remote_url = db.Column(db.String(400), nullable=True)
    sync_token = db.Column(db.String(120), nullable=True)
    last_synced_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    companies = db.relationship(
        "Company", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    clients = db.relationship(
        "Client", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    projects = db.relationship(
        "Project", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    templates = db.relationship(
        "WorkflowTemplate", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    courses = db.relationship(
        "Course", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    products = db.relationship(
        "DigitalProduct", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    checklist_templates = db.relationship(
        "ChecklistTemplate", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    reminders = db.relationship(
        "Reminder", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    equipment = db.relationship(
        "Equipment", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    equipment_checkouts = db.relationship(
        "EquipmentCheckout", backref="owner", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def set_recovery_code(self, code: str) -> None:
        self.recovery_code_hash = generate_password_hash(code)

    def check_recovery_code(self, code: str) -> bool:
        if not self.recovery_code_hash:
            return False
        return check_password_hash(self.recovery_code_hash, code)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "language": self.language,
            "theme": self.theme,
            "currency": self.currency,
            "sync_remote_url": self.sync_remote_url,
            "sync_configured": bool(self.sync_remote_url and self.sync_token),
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
        }


class WebAuthnCredential(db.Model):
    """O credentiala Touch ID / Windows Hello inregistrata pentru un cont,
    pe un calculator anume - autentificare rapida, fara sa mai tastezi
    parola. Parola ramane mereu functionala ca fallback."""
    __tablename__ = "webauthn_credentials"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    credential_id = db.Column(db.String(400), unique=True, nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    sign_count = db.Column(db.Integer, nullable=False, default=0)
    label = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("webauthn_credentials", lazy=True, cascade="all, delete-orphan"))


class Company(db.Model):
    """A firm/business, with full fiscal details - distinct from the
    individual people (Client rows) who work there. A Client optionally
    points at one Company via `company_id`; the firm itself never has a
    single "email/phone" of its own here, on purpose - you always reach
    a specific person, per Cristi's ask ("colaborare la prima mână")."""

    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    cui = db.Column(db.String(50), nullable=True)
    fiscal_address = db.Column(db.String(400), nullable=True)
    headquarters_address = db.Column(db.String(400), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # backref name "company_obj" (not "company") deliberately avoids
    # colliding with Client.company, the older free-text field kept for
    # backward compatibility.
    contacts = db.relationship("Client", backref="company_obj", lazy=True)

    def to_dict(self, include_contacts=False) -> dict:
        all_projects = [p for c in self.contacts for p in c.projects]
        data = {
            "id": self.id,
            "name": self.name,
            "cui": self.cui,
            "fiscal_address": self.fiscal_address,
            "headquarters_address": self.headquarters_address,
            "notes": self.notes,
            "contact_count": len(self.contacts),
            "payment_status": _worst_payment_status(all_projects),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_contacts:
            data["contacts"] = [c.to_dict() for c in self.contacts]
        return data


class Client(db.Model):
    """A contact PERSON - historically the only entity here (hence the
    legacy `company` free-text field), now optionally linked to a full
    Company record via `company_id`, with a `role` (department/title) at
    that company."""

    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)

    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship("Project", backref="client", lazy=True)
    courses = db.relationship("Course", backref="client", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "company": self.company,
            "company_id": self.company_id,
            "company_name": self.company_obj.name if self.company_obj else None,
            "role": self.role,
            "email": self.email,
            "phone": self.phone,
            "notes": self.notes,
            "project_count": len(self.projects),
            "course_count": len(self.courses),
            "payment_status": _worst_payment_status(self.projects),
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


class Attachment(db.Model):
    """A file attached to a project (contract, brief, reference), stored
    locally under the app's per-user data directory — never uploaded anywhere."""

    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    filename = db.Column(db.String(300), nullable=False)
    stored_name = db.Column(db.String(120), nullable=False)  # name on disk
    size_bytes = db.Column(db.Integer, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "filename": self.filename,
            "size_bytes": self.size_bytes,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
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
    currency = db.Column(db.String(3), nullable=False, default="EUR")

    notes = db.Column(db.Text, nullable=True)
    # One free-text note per pipeline stage, e.g. {"planning": "...", "filming": "...", ...}
    stage_notes = db.Column(db.JSON, nullable=True, default=dict)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attachments = db.relationship(
        "Attachment", backref="project", lazy=True, cascade="all, delete-orphan"
    )
    checklists = db.relationship(
        "Checklist", backref="project", lazy=True, cascade="all, delete-orphan"
    )
    reminders = db.relationship(
        "Reminder", backref="project", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, include_attachments=False, include_checklists=False) -> dict:
        data = {
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
            "currency": self.currency,
            "notes": self.notes,
            "stage_notes": self.stage_notes or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "attachment_count": len(self.attachments),
            "checklist_count": len(self.checklists),
        }
        if include_attachments:
            data["attachments"] = [a.to_dict() for a in self.attachments]
        if include_checklists:
            data["checklists"] = [cl.to_dict() for cl in self.checklists]
        return data


class Course(db.Model):
    """A 1-on-1 training session (e.g. color grading coaching)."""

    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=True)

    topic = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(5), nullable=True)  # "HH:MM"
    duration_minutes = db.Column(db.Integer, nullable=True, default=60)

    price = db.Column(db.Float, nullable=True, default=0)
    currency = db.Column(db.String(3), nullable=False, default="EUR")
    paid = db.Column(db.Boolean, nullable=False, default=False)
    payment_date = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="scheduled")
    location = db.Column(db.String(20), nullable=False, default="online")
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "client_id": self.client_id,
            "client_name": self.client.name if self.client else None,
            "topic": self.topic,
            "date": self.date.isoformat() if self.date else None,
            "time": self.time,
            "duration_minutes": self.duration_minutes,
            "price": self.price,
            "currency": self.currency,
            "paid": self.paid,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "status": self.status,
            "location": self.location,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DigitalProduct(db.Model):
    """A sellable digital asset: DCTL, PowerGrade, LUT pack, preset, template…"""

    __tablename__ = "digital_products"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    product_type = db.Column(db.String(30), nullable=False, default="other")
    description = db.Column(db.Text, nullable=True)

    price = db.Column(db.Float, nullable=True, default=0)
    currency = db.Column(db.String(3), nullable=False, default="EUR")
    file_path = db.Column(db.String(500), nullable=True)
    download_link = db.Column(db.String(500), nullable=True)
    version = db.Column(db.String(30), nullable=True)
    compatibility = db.Column(db.String(150), nullable=True)

    units_sold = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "product_type": self.product_type,
            "description": self.description,
            "price": self.price,
            "currency": self.currency,
            "file_path": self.file_path,
            "download_link": self.download_link,
            "version": self.version,
            "compatibility": self.compatibility,
            "units_sold": self.units_sold,
            "revenue": round((self.price or 0) * (self.units_sold or 0), 2),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ChecklistTemplate(db.Model):
    """A reusable checklist blueprint, e.g. 'Pre-filmare nuntă'. `items` is a
    plain list of strings — each becomes a fresh, unchecked item whenever the
    template is applied to a project."""

    __tablename__ = "checklist_templates"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(150), nullable=False)
    checklist_type = db.Column(db.String(20), nullable=False, default="general")
    project_type = db.Column(db.String(30), nullable=True)
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    items = db.Column(db.JSON, nullable=True, default=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "checklist_type": self.checklist_type,
            "project_type": self.project_type,
            "is_default": self.is_default,
            "items": self.items or [],
        }


class Checklist(db.Model):
    """A concrete checklist attached to one project. `items` is a list of
    {"id": "...", "text": "...", "done": bool} dicts."""

    __tablename__ = "checklists"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey("checklist_templates.id"), nullable=True)

    name = db.Column(db.String(150), nullable=False)
    checklist_type = db.Column(db.String(20), nullable=False, default="general")
    items = db.Column(db.JSON, nullable=True, default=list)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        items = self.items or []
        done_count = sum(1 for it in items if it.get("done"))
        return {
            "id": self.id,
            "project_id": self.project_id,
            "template_id": self.template_id,
            "name": self.name,
            "checklist_type": self.checklist_type,
            "items": items,
            "done_count": done_count,
            "total_count": len(items),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Reminder(db.Model):
    """A standalone reminder — a deadline, an unpaid invoice follow-up, a
    meeting — optionally linked to a project."""

    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    due_time = db.Column(db.String(5), nullable=True)  # "HH:MM"
    reminder_type = db.Column(db.String(20), nullable=False, default="general")
    done = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_title": self.project.title if self.project else None,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "due_time": self.due_time,
            "reminder_type": self.reminder_type,
            "done": self.done,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Equipment(db.Model):
    """One physical gear item (camera, lens, light, mic…), tracked
    individually so a checkout sheet can name it and its status stays
    accurate as it moves in and out of storage."""

    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="available")
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "serial_number": self.serial_number,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class EquipmentCheckout(db.Model):
    """One handoff sheet: a batch of equipment given to a crew for a
    project, checked back in item-by-item. `items` is a list of
    {"equipment_id": int, "returned": bool} dicts — same JSON-list-of-
    dicts shape as Checklist.items, so it can be toggled the same way."""

    __tablename__ = "equipment_checkouts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)

    items = db.Column(db.JSON, nullable=False, default=list)
    notes = db.Column(db.Text, nullable=True)

    checked_out_at = db.Column(db.DateTime, default=datetime.utcnow)
    returned_at = db.Column(db.DateTime, nullable=True)

    project = db.relationship("Project", backref=db.backref("equipment_checkouts", lazy=True))

    def to_dict(self) -> dict:
        items = self.items or []
        equipment_ids = [it.get("equipment_id") for it in items]
        equipment_by_id = {
            e.id: e for e in Equipment.query.filter(Equipment.id.in_(equipment_ids)).all()
        } if equipment_ids else {}
        enriched_items = [
            {
                "equipment_id": it.get("equipment_id"),
                "equipment_name": equipment_by_id[it["equipment_id"]].name
                if it.get("equipment_id") in equipment_by_id else None,
                "returned": bool(it.get("returned")),
            }
            for it in items
        ]
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_title": self.project.title if self.project else None,
            "items": enriched_items,
            "returned_count": sum(1 for it in items if it.get("returned")),
            "total_count": len(items),
            "notes": self.notes,
            "checked_out_at": self.checked_out_at.isoformat() if self.checked_out_at else None,
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
        }
