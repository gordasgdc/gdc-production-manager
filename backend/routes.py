"""
GDC Production Manager - API routes for clients, projects, templates, dashboard.
"""

import os
import uuid
import copy
from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from models import (
    db, Client, Project, WorkflowTemplate, Attachment, Course, DigitalProduct,
    ChecklistTemplate, Checklist, Reminder,
    PROJECT_STATUSES, PROJECT_TYPES, PAYMENT_STATUSES, COURSE_STATUSES, PRODUCT_TYPES,
    CURRENCIES, CHECKLIST_TYPES, REMINDER_TYPES,
)
from auth import login_required, current_user
from config import ATTACHMENTS_DIR

api_bp = Blueprint("api", __name__)


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------- meta -----

@api_bp.route("/api/meta", methods=["GET"])
@login_required
def meta():
    return jsonify(
        {
            "statuses": PROJECT_STATUSES,
            "project_types": PROJECT_TYPES,
            "payment_statuses": PAYMENT_STATUSES,
            "course_statuses": COURSE_STATUSES,
            "product_types": PRODUCT_TYPES,
            "currencies": CURRENCIES,
            "checklist_types": CHECKLIST_TYPES,
            "reminder_types": REMINDER_TYPES,
        }
    )


# ------------------------------------------------------------- clients -----

@api_bp.route("/api/clients", methods=["GET"])
@login_required
def list_clients():
    user = current_user()
    q = (request.args.get("q") or "").strip().lower()
    clients = Client.query.filter_by(user_id=user.id).order_by(Client.name.asc()).all()
    if q:
        clients = [c for c in clients if q in (c.name or "").lower() or q in (c.company or "").lower()]
    return jsonify([c.to_dict() for c in clients])


@api_bp.route("/api/clients", methods=["POST"])
@login_required
def create_client():
    user = current_user()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name_required"}), 400

    client = Client(
        user_id=user.id,
        name=name,
        company=data.get("company"),
        email=data.get("email"),
        phone=data.get("phone"),
        notes=data.get("notes"),
    )
    db.session.add(client)
    db.session.commit()
    return jsonify(client.to_dict()), 201


@api_bp.route("/api/clients/<int:client_id>", methods=["PUT"])
@login_required
def update_client(client_id):
    user = current_user()
    client = Client.query.filter_by(id=client_id, user_id=user.id).first()
    if not client:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    for field in ("name", "company", "email", "phone", "notes"):
        if field in data:
            setattr(client, field, data[field])
    db.session.commit()
    return jsonify(client.to_dict())


@api_bp.route("/api/clients/<int:client_id>", methods=["DELETE"])
@login_required
def delete_client(client_id):
    user = current_user()
    client = Client.query.filter_by(id=client_id, user_id=user.id).first()
    if not client:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(client)
    db.session.commit()
    return jsonify({"ok": True})


# ------------------------------------------------------------ templates ----

@api_bp.route("/api/templates", methods=["GET"])
@login_required
def list_templates():
    user = current_user()
    templates = WorkflowTemplate.query.filter_by(user_id=user.id).all()
    return jsonify([t.to_dict() for t in templates])


@api_bp.route("/api/templates", methods=["POST"])
@login_required
def create_template():
    user = current_user()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name_required"}), 400
    stages = data.get("stages") or []
    template = WorkflowTemplate(
        user_id=user.id,
        name=name,
        project_type=data.get("project_type"),
        stages=",".join(stages) if isinstance(stages, list) else stages,
    )
    db.session.add(template)
    db.session.commit()
    return jsonify(template.to_dict()), 201


@api_bp.route("/api/templates/<int:template_id>", methods=["DELETE"])
@login_required
def delete_template(template_id):
    user = current_user()
    template = WorkflowTemplate.query.filter_by(id=template_id, user_id=user.id).first()
    if not template:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(template)
    db.session.commit()
    return jsonify({"ok": True})


# ------------------------------------------------------------- projects ----

@api_bp.route("/api/projects", methods=["GET"])
@login_required
def list_projects():
    user = current_user()
    query = Project.query.filter_by(user_id=user.id)

    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)

    client_id = request.args.get("client_id")
    if client_id:
        query = query.filter_by(client_id=client_id)

    q = (request.args.get("q") or "").strip().lower()

    projects = query.order_by(Project.updated_at.desc()).all()
    if q:
        projects = [p for p in projects if q in (p.title or "").lower()]

    return jsonify([p.to_dict() for p in projects])


@api_bp.route("/api/projects/<int:project_id>", methods=["GET"])
@login_required
def get_project(project_id):
    user = current_user()
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({"error": "not_found"}), 404
    return jsonify(project.to_dict(include_attachments=True, include_checklists=True))


@api_bp.route("/api/projects", methods=["POST"])
@login_required
def create_project():
    user = current_user()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title_required"}), 400

    project = Project(
        user_id=user.id,
        title=title,
        project_type=data.get("project_type") or "other",
        status=data.get("status") or "planning",
        client_id=data.get("client_id") or None,
        template_id=data.get("template_id") or None,
        shoot_location=data.get("shoot_location"),
        shoot_date=parse_date(data.get("shoot_date")),
        delivery_date=parse_date(data.get("delivery_date")),
        path_raw=data.get("path_raw"),
        path_edit=data.get("path_edit"),
        path_export=data.get("path_export"),
        budget_total=data.get("budget_total") or 0,
        amount_paid=data.get("amount_paid") or 0,
        payment_status=data.get("payment_status") or "unpaid",
        currency=data.get("currency") if data.get("currency") in CURRENCIES else user.currency,
        notes=data.get("notes"),
        stage_notes={},
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@api_bp.route("/api/projects/<int:project_id>", methods=["PUT"])
@login_required
def update_project(project_id):
    user = current_user()
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    simple_fields = (
        "title", "project_type", "status", "client_id", "template_id",
        "shoot_location", "path_raw", "path_edit", "path_export",
        "budget_total", "amount_paid", "payment_status", "notes",
    )
    for field in simple_fields:
        if field in data:
            setattr(project, field, data[field])

    if "currency" in data and data["currency"] in CURRENCIES:
        project.currency = data["currency"]

    if "shoot_date" in data:
        project.shoot_date = parse_date(data.get("shoot_date"))
    if "delivery_date" in data:
        project.delivery_date = parse_date(data.get("delivery_date"))

    project.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(project.to_dict())


@api_bp.route("/api/projects/<int:project_id>/next-step", methods=["POST"])
@login_required
def next_step(project_id):
    """Advances the project to the next stage in the pipeline. No-op (200,
    unchanged) if it's already at the last stage."""
    user = current_user()
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({"error": "not_found"}), 404

    try:
        idx = PROJECT_STATUSES.index(project.status)
    except ValueError:
        idx = 0

    if idx < len(PROJECT_STATUSES) - 1:
        project.status = PROJECT_STATUSES[idx + 1]
        project.updated_at = datetime.utcnow()
        db.session.commit()

    return jsonify(project.to_dict())


@api_bp.route("/api/projects/<int:project_id>/stage-notes", methods=["PUT"])
@login_required
def update_stage_notes(project_id):
    """Updates the note for a single pipeline stage without touching the
    others, e.g. {"status": "editing", "note": "..."}."""
    user = current_user()
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    stage = data.get("status")
    note = data.get("note", "")
    if stage not in PROJECT_STATUSES:
        return jsonify({"error": "invalid_status"}), 400

    stage_notes = dict(project.stage_notes or {})
    stage_notes[stage] = note
    project.stage_notes = stage_notes
    project.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(project.to_dict())


@api_bp.route("/api/projects/<int:project_id>", methods=["DELETE"])
@login_required
def delete_project(project_id):
    user = current_user()
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({"ok": True})


# ------------------------------------------------------------ dashboard ----

@api_bp.route("/api/dashboard", methods=["GET"])
@api_bp.route("/api/stats", methods=["GET"])
@login_required
def dashboard():
    user = current_user()
    projects = Project.query.filter_by(user_id=user.id).all()

    by_status = {s: 0 for s in PROJECT_STATUSES}
    active_count = 0
    # Budgets are tracked per currency rather than summed together, since
    # mixing EUR and RON totals would be meaningless.
    totals_by_currency = {}
    upcoming_deliveries = []
    today = date.today()

    for p in projects:
        by_status[p.status] = by_status.get(p.status, 0) + 1
        if p.status != "delivered":
            active_count += 1

        cur = p.currency or user.currency
        bucket = totals_by_currency.setdefault(cur, {"budget": 0.0, "paid": 0.0})
        bucket["budget"] += p.budget_total or 0
        bucket["paid"] += p.amount_paid or 0

        if p.delivery_date and p.delivery_date >= today and p.status != "delivered":
            upcoming_deliveries.append(p)

    upcoming_deliveries.sort(key=lambda p: p.delivery_date)
    for cur, bucket in totals_by_currency.items():
        bucket["outstanding"] = max(bucket["budget"] - bucket["paid"], 0)

    primary = totals_by_currency.get(user.currency, {"budget": 0, "paid": 0, "outstanding": 0})

    # ---- courses ----
    courses = Course.query.filter_by(user_id=user.id).all()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    courses_this_week = [c for c in courses if c.date and week_start <= c.date <= week_end]
    upcoming_courses = sorted(
        [c for c in courses if c.date and c.date >= today and c.status not in ("completed", "cancelled")],
        key=lambda c: (c.date, c.time or ""),
    )

    course_revenue_by_currency = {}
    for c in courses:
        if c.paid and c.date and c.date.year == today.year and c.date.month == today.month:
            cur = c.currency or user.currency
            course_revenue_by_currency[cur] = course_revenue_by_currency.get(cur, 0) + (c.price or 0)

    # ---- digital products ----
    products = DigitalProduct.query.filter_by(user_id=user.id).all()
    product_revenue_by_currency = {}
    for pr in products:
        cur = pr.currency or user.currency
        product_revenue_by_currency[cur] = product_revenue_by_currency.get(cur, 0) + (pr.price or 0) * (pr.units_sold or 0)

    # ---- reminders ----
    reminder_horizon = today + timedelta(days=7)
    reminders = (
        Reminder.query.filter_by(user_id=user.id, done=False)
        .filter(Reminder.due_date <= reminder_horizon)
        .order_by(Reminder.due_date.asc())
        .limit(8)
        .all()
    )

    return jsonify(
        {
            "total_projects": len(projects),
            "active_projects": active_count,
            "total_clients": Client.query.filter_by(user_id=user.id).count(),
            "by_status": by_status,
            "primary_currency": user.currency,
            "total_budget": primary["budget"],
            "total_paid": primary["paid"],
            "outstanding": primary["outstanding"],
            "totals_by_currency": totals_by_currency,
            "upcoming_deliveries": [p.to_dict() for p in upcoming_deliveries[:5]],

            "total_courses": len(courses),
            "courses_this_week": len(courses_this_week),
            "upcoming_courses": [c.to_dict() for c in upcoming_courses[:5]],
            "course_revenue_this_month_by_currency": course_revenue_by_currency,

            "total_products": len(products),
            "product_revenue_total_by_currency": product_revenue_by_currency,

            "upcoming_reminders": [r.to_dict() for r in reminders],
        }
    )


# --------------------------------------------------------- notifications ---

@api_bp.route("/api/notifications", methods=["GET"])
@login_required
def notifications():
    """Lightweight, computed-on-read notifications: nothing is stored or
    pushed — just deadlines and unpaid invoices worth surfacing right now."""
    user = current_user()
    projects = Project.query.filter_by(user_id=user.id).all()
    today = date.today()

    items = []
    for p in projects:
        if p.status == "delivered":
            continue
        if p.delivery_date:
            days = (p.delivery_date - today).days
            if 0 <= days <= 3:
                items.append({
                    "type": "deadline_soon",
                    "project_id": p.id,
                    "project_title": p.title,
                    "days": days,
                    "delivery_date": p.delivery_date.isoformat(),
                })
            elif days < 0:
                items.append({
                    "type": "deadline_overdue",
                    "project_id": p.id,
                    "project_title": p.title,
                    "days": abs(days),
                    "delivery_date": p.delivery_date.isoformat(),
                })
        if p.payment_status != "paid" and (p.budget_total or 0) > 0:
            outstanding = (p.budget_total or 0) - (p.amount_paid or 0)
            if outstanding > 0 and p.status in ("review", "final", "delivered"):
                items.append({
                    "type": "payment_outstanding",
                    "project_id": p.id,
                    "project_title": p.title,
                    "amount": outstanding,
                })

    return jsonify({"notifications": items})


# --------------------------------------------------------- export/import ---

def build_export_dict(user) -> dict:
    clients = Client.query.filter_by(user_id=user.id).all()
    projects = Project.query.filter_by(user_id=user.id).all()
    templates = WorkflowTemplate.query.filter_by(user_id=user.id).all()

    return {
        "export_version": 1,
        "exported_at": datetime.utcnow().isoformat(),
        "username": user.username,
        "clients": [c.to_dict() for c in clients],
        "projects": [p.to_dict() for p in projects],
        "templates": [t.to_dict() for t in templates],
    }


def apply_import_payload(user, payload: dict) -> dict:
    id_map = {}
    imported_clients = 0
    imported_projects = 0

    for c in payload.get("clients", []):
        client = Client(
            user_id=user.id,
            name=c.get("name") or "—",
            company=c.get("company"),
            email=c.get("email"),
            phone=c.get("phone"),
            notes=c.get("notes"),
        )
        db.session.add(client)
        db.session.flush()
        if c.get("id") is not None:
            id_map[c["id"]] = client.id
        imported_clients += 1

    for p in payload.get("projects", []):
        old_client_id = p.get("client_id")
        project = Project(
            user_id=user.id,
            title=p.get("title") or "—",
            project_type=p.get("project_type") or "other",
            status=p.get("status") or "planning",
            client_id=id_map.get(old_client_id) if old_client_id else None,
            shoot_location=p.get("shoot_location"),
            shoot_date=parse_date(p.get("shoot_date")),
            delivery_date=parse_date(p.get("delivery_date")),
            path_raw=p.get("path_raw"),
            path_edit=p.get("path_edit"),
            path_export=p.get("path_export"),
            budget_total=p.get("budget_total") or 0,
            amount_paid=p.get("amount_paid") or 0,
            payment_status=p.get("payment_status") or "unpaid",
            notes=p.get("notes"),
        )
        db.session.add(project)
        imported_projects += 1

    db.session.commit()
    return {"imported_clients": imported_clients, "imported_projects": imported_projects}


@api_bp.route("/api/export", methods=["GET"])
@login_required
def export_data():
    user = current_user()
    return jsonify(build_export_dict(user))


@api_bp.route("/api/import", methods=["POST"])
@login_required
def import_data():
    """Imports a previously exported JSON snapshot. Client/project ids from
    the file are remapped to new rows for this account — nothing is
    overwritten, so importing twice just duplicates data (safe by default)."""
    user = current_user()
    payload = request.get_json(silent=True) or {}

    if "clients" not in payload and "projects" not in payload:
        return jsonify({"error": "invalid_file"}), 400

    result = apply_import_payload(user, payload)
    return jsonify(result)


# ---------------------------------------------------------- attachments ----

ALLOWED_ATTACHMENT_EXTENSIONS = {
    "pdf", "doc", "docx", "txt", "rtf", "odt",
    "jpg", "jpeg", "png", "heic", "gif", "webp",
    "zip", "csv", "xlsx",
}


def _attachment_dir(project_id: int) -> str:
    path = os.path.join(ATTACHMENTS_DIR, str(project_id))
    os.makedirs(path, exist_ok=True)
    return path


@api_bp.route("/api/projects/<int:project_id>/attachments", methods=["GET"])
@login_required
def list_attachments(project_id):
    user = current_user()
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({"error": "not_found"}), 404
    return jsonify([a.to_dict() for a in project.attachments])


@api_bp.route("/api/projects/<int:project_id>/attachments", methods=["POST"])
@login_required
def upload_attachment(project_id):
    user = current_user()
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({"error": "not_found"}), 404

    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "no_file"}), 400

    original_name = secure_filename(file.filename)
    ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        return jsonify({"error": "file_type_not_allowed"}), 400

    stored_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    dest_dir = _attachment_dir(project_id)
    dest_path = os.path.join(dest_dir, stored_name)
    file.save(dest_path)

    attachment = Attachment(
        project_id=project_id,
        filename=original_name,
        stored_name=stored_name,
        size_bytes=os.path.getsize(dest_path),
    )
    db.session.add(attachment)
    db.session.commit()
    return jsonify(attachment.to_dict()), 201


@api_bp.route("/api/attachments/<int:attachment_id>/download", methods=["GET"])
@login_required
def download_attachment(attachment_id):
    user = current_user()
    attachment = (
        Attachment.query
        .join(Project, Attachment.project_id == Project.id)
        .filter(Attachment.id == attachment_id, Project.user_id == user.id)
        .first()
    )
    if not attachment:
        return jsonify({"error": "not_found"}), 404
    directory = _attachment_dir(attachment.project_id)
    return send_from_directory(directory, attachment.stored_name, download_name=attachment.filename, as_attachment=True)


@api_bp.route("/api/attachments/<int:attachment_id>", methods=["DELETE"])
@login_required
def delete_attachment(attachment_id):
    user = current_user()
    attachment = (
        Attachment.query
        .join(Project, Attachment.project_id == Project.id)
        .filter(Attachment.id == attachment_id, Project.user_id == user.id)
        .first()
    )
    if not attachment:
        return jsonify({"error": "not_found"}), 404

    file_path = os.path.join(_attachment_dir(attachment.project_id), attachment.stored_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

    db.session.delete(attachment)
    db.session.commit()
    return jsonify({"ok": True})


# -------------------------------------------------------------- courses ----

@api_bp.route("/api/courses", methods=["GET"])
@login_required
def list_courses():
    user = current_user()
    query = Course.query.filter_by(user_id=user.id)

    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)

    courses = query.order_by(Course.date.asc()).all()
    return jsonify([c.to_dict() for c in courses])


@api_bp.route("/api/clients/<int:client_id>/courses", methods=["GET"])
@login_required
def list_client_courses(client_id):
    user = current_user()
    client = Client.query.filter_by(id=client_id, user_id=user.id).first()
    if not client:
        return jsonify({"error": "not_found"}), 404
    courses = Course.query.filter_by(user_id=user.id, client_id=client_id).order_by(Course.date.asc()).all()
    return jsonify([c.to_dict() for c in courses])


@api_bp.route("/api/courses/<int:course_id>", methods=["GET"])
@login_required
def get_course(course_id):
    user = current_user()
    course = Course.query.filter_by(id=course_id, user_id=user.id).first()
    if not course:
        return jsonify({"error": "not_found"}), 404
    return jsonify(course.to_dict())


@api_bp.route("/api/courses", methods=["POST"])
@login_required
def create_course():
    user = current_user()
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "").strip()
    course_date = parse_date(data.get("date"))
    if not topic:
        return jsonify({"error": "topic_required"}), 400
    if not course_date:
        return jsonify({"error": "date_required"}), 400

    course = Course(
        user_id=user.id,
        client_id=data.get("client_id") or None,
        topic=topic,
        date=course_date,
        time=data.get("time"),
        duration_minutes=data.get("duration_minutes") or 60,
        price=data.get("price") or 0,
        currency=data.get("currency") if data.get("currency") in CURRENCIES else user.currency,
        paid=bool(data.get("paid")),
        payment_date=parse_date(data.get("payment_date")),
        status=data.get("status") if data.get("status") in COURSE_STATUSES else "scheduled",
        location=data.get("location") or "online",
        notes=data.get("notes"),
    )
    db.session.add(course)
    db.session.commit()
    return jsonify(course.to_dict()), 201


@api_bp.route("/api/courses/<int:course_id>", methods=["PUT"])
@login_required
def update_course(course_id):
    user = current_user()
    course = Course.query.filter_by(id=course_id, user_id=user.id).first()
    if not course:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    simple_fields = ("topic", "time", "duration_minutes", "price", "location", "notes")
    for field in simple_fields:
        if field in data:
            setattr(course, field, data[field])

    if "client_id" in data:
        course.client_id = data.get("client_id") or None
    if "currency" in data and data["currency"] in CURRENCIES:
        course.currency = data["currency"]
    if "status" in data and data["status"] in COURSE_STATUSES:
        course.status = data["status"]
    if "date" in data:
        parsed = parse_date(data.get("date"))
        if parsed:
            course.date = parsed
    if "paid" in data:
        course.paid = bool(data["paid"])
    if "payment_date" in data:
        course.payment_date = parse_date(data.get("payment_date"))

    db.session.commit()
    return jsonify(course.to_dict())


@api_bp.route("/api/courses/<int:course_id>", methods=["DELETE"])
@login_required
def delete_course(course_id):
    user = current_user()
    course = Course.query.filter_by(id=course_id, user_id=user.id).first()
    if not course:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(course)
    db.session.commit()
    return jsonify({"ok": True})


# -------------------------------------------------------------- products ---

@api_bp.route("/api/products", methods=["GET"])
@login_required
def list_products():
    user = current_user()
    q = (request.args.get("q") or "").strip().lower()
    products = DigitalProduct.query.filter_by(user_id=user.id).order_by(DigitalProduct.name.asc()).all()
    if q:
        products = [p for p in products if q in p.name.lower()]
    return jsonify([p.to_dict() for p in products])


@api_bp.route("/api/products/<int:product_id>", methods=["GET"])
@login_required
def get_product(product_id):
    user = current_user()
    product = DigitalProduct.query.filter_by(id=product_id, user_id=user.id).first()
    if not product:
        return jsonify({"error": "not_found"}), 404
    return jsonify(product.to_dict())


@api_bp.route("/api/products", methods=["POST"])
@login_required
def create_product():
    user = current_user()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name_required"}), 400

    product = DigitalProduct(
        user_id=user.id,
        name=name,
        product_type=data.get("product_type") if data.get("product_type") in PRODUCT_TYPES else "other",
        description=data.get("description"),
        price=data.get("price") or 0,
        currency=data.get("currency") if data.get("currency") in CURRENCIES else user.currency,
        file_path=data.get("file_path"),
        download_link=data.get("download_link"),
        version=data.get("version"),
        compatibility=data.get("compatibility"),
        units_sold=data.get("units_sold") or 0,
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@api_bp.route("/api/products/<int:product_id>", methods=["PUT"])
@login_required
def update_product(product_id):
    user = current_user()
    product = DigitalProduct.query.filter_by(id=product_id, user_id=user.id).first()
    if not product:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    simple_fields = (
        "name", "description", "price", "file_path", "download_link",
        "version", "compatibility", "units_sold",
    )
    for field in simple_fields:
        if field in data:
            setattr(product, field, data[field])

    if "product_type" in data and data["product_type"] in PRODUCT_TYPES:
        product.product_type = data["product_type"]
    if "currency" in data and data["currency"] in CURRENCIES:
        product.currency = data["currency"]

    product.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(product.to_dict())


@api_bp.route("/api/products/<int:product_id>", methods=["DELETE"])
@login_required
def delete_product(product_id):
    user = current_user()
    product = DigitalProduct.query.filter_by(id=product_id, user_id=user.id).first()
    if not product:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"ok": True})


# ------------------------------------------------------ checklist templates

@api_bp.route("/api/checklist-templates", methods=["GET"])
@login_required
def list_checklist_templates():
    user = current_user()
    templates = ChecklistTemplate.query.filter_by(user_id=user.id).order_by(ChecklistTemplate.name.asc()).all()
    return jsonify([t.to_dict() for t in templates])


@api_bp.route("/api/checklist-templates", methods=["POST"])
@login_required
def create_checklist_template():
    user = current_user()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name_required"}), 400

    items = data.get("items") or []
    if not isinstance(items, list):
        items = []

    template = ChecklistTemplate(
        user_id=user.id,
        name=name,
        checklist_type=data.get("checklist_type") if data.get("checklist_type") in CHECKLIST_TYPES else "general",
        items=[str(i).strip() for i in items if str(i).strip()],
    )
    db.session.add(template)
    db.session.commit()
    return jsonify(template.to_dict()), 201


@api_bp.route("/api/checklist-templates/<int:template_id>", methods=["PUT"])
@login_required
def update_checklist_template(template_id):
    user = current_user()
    template = ChecklistTemplate.query.filter_by(id=template_id, user_id=user.id).first()
    if not template:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data and data["name"].strip():
        template.name = data["name"].strip()
    if "checklist_type" in data and data["checklist_type"] in CHECKLIST_TYPES:
        template.checklist_type = data["checklist_type"]
    if "items" in data and isinstance(data["items"], list):
        template.items = [str(i).strip() for i in data["items"] if str(i).strip()]

    db.session.commit()
    return jsonify(template.to_dict())


@api_bp.route("/api/checklist-templates/<int:template_id>", methods=["DELETE"])
@login_required
def delete_checklist_template(template_id):
    user = current_user()
    template = ChecklistTemplate.query.filter_by(id=template_id, user_id=user.id).first()
    if not template:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(template)
    db.session.commit()
    return jsonify({"ok": True})


# ----------------------------------------------------------- checklists ---

def _project_or_404(user, project_id):
    return Project.query.filter_by(id=project_id, user_id=user.id).first()


@api_bp.route("/api/projects/<int:project_id>/checklists", methods=["GET"])
@login_required
def list_project_checklists(project_id):
    user = current_user()
    project = _project_or_404(user, project_id)
    if not project:
        return jsonify({"error": "not_found"}), 404
    return jsonify([cl.to_dict() for cl in project.checklists])


@api_bp.route("/api/projects/<int:project_id>/checklists", methods=["POST"])
@login_required
def create_checklist(project_id):
    user = current_user()
    project = _project_or_404(user, project_id)
    if not project:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    template_id = data.get("template_id")
    items_source = data.get("items") or []

    name = (data.get("name") or "").strip()
    checklist_type = data.get("checklist_type") if data.get("checklist_type") in CHECKLIST_TYPES else "general"

    if template_id:
        template = ChecklistTemplate.query.filter_by(id=template_id, user_id=user.id).first()
        if template:
            items_source = template.items or []
            if not name:
                name = template.name
            checklist_type = template.checklist_type

    if not name:
        return jsonify({"error": "name_required"}), 400

    items = [{"id": uuid.uuid4().hex[:8], "text": str(t).strip(), "done": False} for t in items_source if str(t).strip()]

    checklist = Checklist(
        project_id=project_id,
        template_id=template_id or None,
        name=name,
        checklist_type=checklist_type,
        items=items,
    )
    db.session.add(checklist)
    db.session.commit()
    return jsonify(checklist.to_dict()), 201


@api_bp.route("/api/checklists/<int:checklist_id>", methods=["PUT"])
@login_required
def update_checklist(checklist_id):
    user = current_user()
    checklist = (
        Checklist.query.join(Project, Checklist.project_id == Project.id)
        .filter(Checklist.id == checklist_id, Project.user_id == user.id)
        .first()
    )
    if not checklist:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data and data["name"].strip():
        checklist.name = data["name"].strip()
    if "checklist_type" in data and data["checklist_type"] in CHECKLIST_TYPES:
        checklist.checklist_type = data["checklist_type"]

    checklist.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(checklist.to_dict())


@api_bp.route("/api/checklists/<int:checklist_id>", methods=["DELETE"])
@login_required
def delete_checklist(checklist_id):
    user = current_user()
    checklist = (
        Checklist.query.join(Project, Checklist.project_id == Project.id)
        .filter(Checklist.id == checklist_id, Project.user_id == user.id)
        .first()
    )
    if not checklist:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(checklist)
    db.session.commit()
    return jsonify({"ok": True})


@api_bp.route("/api/checklists/<int:checklist_id>/items", methods=["POST"])
@login_required
def add_checklist_item(checklist_id):
    user = current_user()
    checklist = (
        Checklist.query.join(Project, Checklist.project_id == Project.id)
        .filter(Checklist.id == checklist_id, Project.user_id == user.id)
        .first()
    )
    if not checklist:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text_required"}), 400

    items = copy.deepcopy(checklist.items or [])
    items.append({"id": uuid.uuid4().hex[:8], "text": text, "done": False})
    checklist.items = items
    checklist.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(checklist.to_dict()), 201


@api_bp.route("/api/checklists/<int:checklist_id>/items/<item_id>", methods=["DELETE"])
@login_required
def delete_checklist_item(checklist_id, item_id):
    user = current_user()
    checklist = (
        Checklist.query.join(Project, Checklist.project_id == Project.id)
        .filter(Checklist.id == checklist_id, Project.user_id == user.id)
        .first()
    )
    if not checklist:
        return jsonify({"error": "not_found"}), 404

    items = [copy.deepcopy(it) for it in (checklist.items or []) if it.get("id") != item_id]
    checklist.items = items
    checklist.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(checklist.to_dict())


@api_bp.route("/api/checklists/<int:checklist_id>/toggle-item", methods=["POST"])
@login_required
def toggle_checklist_item(checklist_id):
    user = current_user()
    checklist = (
        Checklist.query.join(Project, Checklist.project_id == Project.id)
        .filter(Checklist.id == checklist_id, Project.user_id == user.id)
        .first()
    )
    if not checklist:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")

    items = copy.deepcopy(checklist.items or [])
    found = False
    for it in items:
        if it.get("id") == item_id:
            it["done"] = not it.get("done", False)
            found = True
            break

    if not found:
        return jsonify({"error": "item_not_found"}), 404

    checklist.items = items
    checklist.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(checklist.to_dict())


@api_bp.route("/api/checklists/<int:checklist_id>/mark-all", methods=["POST"])
@login_required
def mark_all_checklist_items(checklist_id):
    user = current_user()
    checklist = (
        Checklist.query.join(Project, Checklist.project_id == Project.id)
        .filter(Checklist.id == checklist_id, Project.user_id == user.id)
        .first()
    )
    if not checklist:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    done = data.get("done", True)

    items = copy.deepcopy(checklist.items or [])
    for it in items:
        it["done"] = bool(done)
    checklist.items = items
    checklist.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(checklist.to_dict())


# ------------------------------------------------------------- reminders ---

@api_bp.route("/api/reminders", methods=["GET"])
@login_required
def list_reminders():
    user = current_user()
    query = Reminder.query.filter_by(user_id=user.id)

    done_param = request.args.get("done")
    if done_param is not None:
        query = query.filter_by(done=(done_param == "true"))

    reminders = query.order_by(Reminder.due_date.asc()).all()
    return jsonify([r.to_dict() for r in reminders])


@api_bp.route("/api/reminders/upcoming", methods=["GET"])
@login_required
def upcoming_reminders():
    user = current_user()
    today = date.today()
    horizon = today + timedelta(days=7)
    reminders = (
        Reminder.query.filter_by(user_id=user.id, done=False)
        .filter(Reminder.due_date <= horizon)
        .order_by(Reminder.due_date.asc())
        .all()
    )
    return jsonify([r.to_dict() for r in reminders])


@api_bp.route("/api/reminders", methods=["POST"])
@login_required
def create_reminder():
    user = current_user()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    due_date = parse_date(data.get("due_date"))
    if not title:
        return jsonify({"error": "title_required"}), 400
    if not due_date:
        return jsonify({"error": "due_date_required"}), 400

    reminder = Reminder(
        user_id=user.id,
        project_id=data.get("project_id") or None,
        title=title,
        description=data.get("description"),
        due_date=due_date,
        due_time=data.get("due_time") or None,
        reminder_type=data.get("reminder_type") if data.get("reminder_type") in REMINDER_TYPES else "general",
        done=bool(data.get("done", False)),
    )
    db.session.add(reminder)
    db.session.commit()
    return jsonify(reminder.to_dict()), 201


@api_bp.route("/api/reminders/<int:reminder_id>", methods=["PUT"])
@login_required
def update_reminder(reminder_id):
    user = current_user()
    reminder = Reminder.query.filter_by(id=reminder_id, user_id=user.id).first()
    if not reminder:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    if "title" in data and data["title"].strip():
        reminder.title = data["title"].strip()
    if "description" in data:
        reminder.description = data["description"]
    if "due_date" in data:
        parsed = parse_date(data.get("due_date"))
        if parsed:
            reminder.due_date = parsed
    if "due_time" in data:
        reminder.due_time = data.get("due_time") or None
    if "reminder_type" in data and data["reminder_type"] in REMINDER_TYPES:
        reminder.reminder_type = data["reminder_type"]
    if "project_id" in data:
        reminder.project_id = data.get("project_id") or None
    if "done" in data:
        reminder.done = bool(data["done"])

    db.session.commit()
    return jsonify(reminder.to_dict())


@api_bp.route("/api/reminders/<int:reminder_id>", methods=["DELETE"])
@login_required
def delete_reminder(reminder_id):
    user = current_user()
    reminder = Reminder.query.filter_by(id=reminder_id, user_id=user.id).first()
    if not reminder:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(reminder)
    db.session.commit()
    return jsonify({"ok": True})
