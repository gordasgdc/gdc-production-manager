"""
GDC Production Manager - default data seeded for every new local account.

Currently: a starter set of checklist templates covering the most common
pre/post-shoot scenarios, so a new user isn't starting from a blank page.
They're regular templates once created — the person can freely edit or
delete them, `is_default` is only a label for "came with the app".
"""

from models import db, ChecklistTemplate, ProjectTypeDef, ProjectStageDef, PROJECT_TYPES, PROJECT_STATUSES

# RO labels matching translations.js verbatim (type_*/status_* keys) - the
# frontend still prefers a live t("status_"+key) translation when one
# exists, so EN/ES installs see the correct localized text unchanged; this
# `label` is the fallback (and the only text used for anything the person
# adds/renames later, which has no translation key at all).
_TYPE_LABELS_RO = {
    "film": "Film", "commercial": "Reclamă", "wedding": "Nuntă",
    "documentary": "Documentar", "broadcast": "Broadcast",
    "music_video": "Videoclip muzical", "corporate": "Corporate", "other": "Altul",
}
_STAGE_LABELS_RO = {
    "planning": "Planificare", "filming": "Filmare", "editing": "Montaj",
    "coloring": "Colorizare", "review": "Review", "final": "Final",
    "delivered": "Predat",
}

DEFAULT_CHECKLIST_TEMPLATES = [
    {
        "name": "Pre-filmare Nuntă",
        "checklist_type": "pre_filming",
        "project_type": "wedding",
        "items": [
            "Cameră principală + backup",
            "Obiective (24-70, 70-200, 50mm)",
            "Baterii încărcate (x4)",
            "Carduri (x4)",
            "Trepied + monopod",
            "Lumini (Aputure 300D x2)",
            "Microfoane (lavalier + shotgun)",
            "Căști",
            "Contract semnat",
            "Brief client",
        ],
    },
    {
        "name": "Pre-filmare Reclamă",
        "checklist_type": "pre_filming",
        "project_type": "commercial",
        "items": [
            "Cameră principală",
            "Obiective (24-70, 85mm)",
            "Baterii încărcate",
            "Carduri",
            "Lumini (Aputure 300D + 120D)",
            "Microfoane (shotgun)",
            "Căști",
            "Contract semnat",
            "Storyboard",
        ],
    },
    {
        "name": "Post-filmare Nuntă",
        "checklist_type": "post_filming",
        "project_type": "wedding",
        "items": [
            "Copiază cardurile pe laptop",
            "Verifică integritatea (checksum)",
            "Copiază pe HDD extern (backup)",
            "Cataloghează fișierele",
            "Formatează cardurile",
            "Creează structură foldere (RAW, Edit, Export)",
            "Importă în Resolve",
            "Sincronizează căi fișiere în aplicație",
        ],
    },
    {
        "name": "Post-filmare Reclamă",
        "checklist_type": "post_filming",
        "project_type": "commercial",
        "items": [
            "Copiază cardurile pe laptop",
            "Verifică integritatea (checksum)",
            "Copiază pe HDD extern (backup)",
            "Cataloghează fișierele",
            "Formatează cardurile",
            "Creează structură foldere",
            "Importă în Resolve",
            "Sincronizează căi fișiere",
        ],
    },
]


def seed_default_checklist_templates(user) -> None:
    """Creates the starter checklist templates for a freshly registered
    account. Safe to call multiple times — skips if the user already has
    any default templates (e.g. re-registration edge cases)."""
    already_seeded = ChecklistTemplate.query.filter_by(
        user_id=user.id, is_default=True
    ).first()
    if already_seeded:
        return

    for tpl in DEFAULT_CHECKLIST_TEMPLATES:
        db.session.add(
            ChecklistTemplate(
                user_id=user.id,
                name=tpl["name"],
                checklist_type=tpl["checklist_type"],
                project_type=tpl["project_type"],
                items=list(tpl["items"]),
                is_default=True,
            )
        )
    db.session.commit()


def seed_default_pipeline_defs(user) -> None:
    """v2.0.0: creates the starter ProjectTypeDef/ProjectStageDef rows for
    a user who has none yet - a freshly registered account, or an
    existing one upgrading from pre-2.0.0 (see app.py::_migrate_schema,
    which calls this for every existing user once). Safe to call
    multiple times - skips whichever of the two is already populated,
    so it can't duplicate rows on a second migration pass."""
    if not ProjectTypeDef.query.filter_by(user_id=user.id).first():
        for i, key in enumerate(PROJECT_TYPES):
            db.session.add(ProjectTypeDef(
                user_id=user.id, key=key,
                label=_TYPE_LABELS_RO.get(key, key.replace("_", " ").title()),
                order=i,
            ))
    if not ProjectStageDef.query.filter_by(user_id=user.id).first():
        for i, key in enumerate(PROJECT_STATUSES):
            db.session.add(ProjectStageDef(
                user_id=user.id, key=key,
                label=_STAGE_LABELS_RO.get(key, key.replace("_", " ").title()),
                order=i,
            ))
    db.session.commit()
