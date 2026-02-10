import base64
from flask import Blueprint, current_app, request, Response, render_template, redirect, url_for, send_file
from datetime import datetime
import csv
import io

from .db import get_db

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _check_auth(auth_header: str) -> bool:
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    try:
        b64 = auth_header.split(" ", 1)[1].strip()
        raw = base64.b64decode(b64).decode("utf-8")
        user, pw = raw.split(":", 1)
    except Exception:
        return False

    return user == current_app.config["ADMIN_USER"] and pw == current_app.config["ADMIN_PASS"]


def _auth_required():
    return Response(
        "Acceso restringido",
        401,
        {"WWW-Authenticate": 'Basic realm="Admin RSVP"'},
    )


@bp.get("/")
def dashboard():
    if not _check_auth(request.headers.get("Authorization")):
        return _auth_required()

    db = get_db()
    invites = db.execute(
        "SELECT id, code, label, max_guests, is_active, created_at FROM invites ORDER BY created_at DESC"
    ).fetchall()
    rsvps = db.execute(
        "SELECT id, invite_code, name, attending, guests_count, allergies, note, created_at FROM rsvps ORDER BY created_at DESC"
    ).fetchall()

    # Stats rápidos
    yes_total = sum(r["guests_count"] for r in rsvps if r["attending"] == 1)
    no_count = sum(1 for r in rsvps if r["attending"] == 0)

    return render_template(
        "admin.html",
        invites=invites,
        rsvps=rsvps,
        yes_total=yes_total,
        no_count=no_count,
    )


@bp.post("/invites/create")
def create_invite():
    if not _check_auth(request.headers.get("Authorization")):
        return _auth_required()

    code = (request.form.get("code") or "").strip()
    label = (request.form.get("label") or "").strip()
    max_guests = (request.form.get("max_guests") or "1").strip()

    if not code:
        return redirect(url_for("admin.dashboard"))

    try:
        max_g = max(1, int(max_guests))
    except ValueError:
        max_g = 1

    db = get_db()
    db.execute(
        "INSERT OR REPLACE INTO invites (code, label, max_guests, is_active, created_at) VALUES (?,?,?,?,?)",
        (code, label, max_g, 1, datetime.utcnow().isoformat()),
    )
    db.commit()

    return redirect(url_for("admin.dashboard"))


@bp.post("/invites/toggle")
def toggle_invite():
    if not _check_auth(request.headers.get("Authorization")):
        return _auth_required()

    invite_id = (request.form.get("invite_id") or "").strip()
    if not invite_id.isdigit():
        return redirect(url_for("admin.dashboard"))

    db = get_db()
    row = db.execute("SELECT is_active FROM invites WHERE id = ?", (invite_id,)).fetchone()
    if row is None:
        return redirect(url_for("admin.dashboard"))

    new_val = 0 if row["is_active"] == 1 else 1
    db.execute("UPDATE invites SET is_active = ? WHERE id = ?", (new_val, invite_id))
    db.commit()
    return redirect(url_for("admin.dashboard"))


@bp.get("/export.csv")
def export_csv():
    if not _check_auth(request.headers.get("Authorization")):
        return _auth_required()

    db = get_db()
    rows = db.execute(
        "SELECT invite_code, name, attending, guests_count, allergies, note, created_at FROM rsvps ORDER BY created_at DESC"
    ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["invite_code", "name", "attending", "guests_count", "allergies", "note", "created_at"])
    for r in rows:
        writer.writerow([
            r["invite_code"],
            r["name"],
            "YES" if r["attending"] == 1 else "NO",
            r["guests_count"],
            r["allergies"],
            r["note"],
            r["created_at"],
        ])

    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="rsvps.csv")
