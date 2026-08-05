"""
GDC Production Manager - API routes for clients, projects, templates, dashboard.
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify

from models import db, Client, Project, WorkflowTemplate, PROJECT_STATUSES, PROJECT_TYPES, PAYMENT_STATUSES
from auth import login_required, current_user

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
    return jsonify(project.to_dict())


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
        notes=data.get("notes"),
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

    if "shoot_date" in data:
        project.shoot_date = parse_date(data.get("shoot_date"))
    if "delivery_date" in data:
        project.delivery_date = parse_date(data.get("delivery_date"))

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
@login_required
def dashboard():
    user = current_user()
    projects = Project.query.filter_by(user_id=user.id).all()

    by_status = {s: 0 for s in PROJECT_STATUSES}
    active_count = 0
    total_budget = 0.0
    total_paid = 0.0
    upcoming_deliveries = []
    today = date.today()

    for p in projects:
        by_status[p.status] = by_status.get(p.status, 0) + 1
        if p.status != "delivered":
            active_count += 1
        total_budget += p.budget_total or 0
        total_paid += p.amount_paid or 0
        if p.delivery_date and p.delivery_date >= today and p.status != "delivered":
            upcoming_deliveries.append(p)

    upcoming_deliveries.sort(key=lambda p: p.delivery_date)

    return jsonify(
        {
            "total_projects": len(projects),
            "active_projects": active_count,
            "total_clients": Client.query.filter_by(user_id=user.id).count(),
            "by_status": by_status,
            "total_budget": total_budget,
            "total_paid": total_paid,
            "outstanding": max(total_budget - total_paid, 0),
            "upcoming_deliveries": [p.to_dict() for p in upcoming_deliveries[:5]],
        }
    )
