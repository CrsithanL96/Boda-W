from flask import Blueprint, request, render_template, redirect, url_for, Response
from datetime import datetime

from .db import get_db
from .settings import WEDDING

bp = Blueprint("main", __name__)


@bp.get("/open")
def open_invite():
    code = request.args.get("code","")
    return render_template("intro.html", code=code)


def _get_invite(code: str):
    db = get_db()

    code = (code or "").strip()
    if not code:
        code = "GENERAL"   # <-- clave

    return db.execute(
        "SELECT code, label, max_guests, is_active FROM invites WHERE code = ?",
        (code,),
    ).fetchone()



@bp.get("/")
def home():
    code = (request.args.get("code") or "").strip()
    invite = _get_invite(code)

    # Mostrar intro (sobre) la primera vez que entran con código
    if code and (request.args.get("intro") or "") != "0":
        return redirect(url_for("main.open_invite", code=code))

    # Si quieres permitir acceso general, podrías renderizar sin invite.
    # Aquí, por defecto, mostramos mensaje si no hay code o si es inválido.
    return render_template(
        "index.html",
        W=WEDDING,
        invite=invite,
        code=invite["code"] if invite else code,
        done=False,
        error=None,
    )




@bp.post("/rsvp")
def rsvp():
    code = (request.form.get("code") or "").strip()
    invite = _get_invite(code)

    name = (request.form.get("name") or "").strip()
    attending_raw = (request.form.get("attending") or "").strip()
    guests_raw = (request.form.get("guests_count") or "").strip()
    allergies = (request.form.get("allergies") or "").strip()
    note = (request.form.get("note") or "").strip()

    if not invite or invite["is_active"] != 1:
        return render_template(
            "index.html",
            W=WEDDING,
            invite=None,
            code=code,
            done=False,
            error="Este enlace no parece válido. Revisa el QR o escríbenos por WhatsApp.",
        )

    if not name:
        return render_template(
            "index.html",
            W=WEDDING,
            invite=invite,
            code=code,
            done=False,
            error="Por favor, indica tu nombre y apellidos.",
        )

    if attending_raw not in {"yes", "no"}:
        return render_template(
            "index.html",
            W=WEDDING,
            invite=invite,
            code=code,
            done=False,
            error="Por favor, selecciona si asistirás.",
        )

    try:
        guests_count = int(guests_raw)
    except ValueError:
        guests_count = 0

    max_guests = int(invite["max_guests"])

    # Si no asiste, forzamos 0 o 1? Aquí guardamos 0 para claridad.
    if attending_raw == "no":
        guests_count = 0

    if attending_raw == "yes" and (guests_count < 1 or guests_count > max_guests):
        return render_template(
            "index.html",
            W=WEDDING,
            invite=invite,
            code=code,
            done=False,
            error=f"Para esta invitación puedes confirmar entre 1 y {max_guests} asistentes.",
        )

    attending = 1 if attending_raw == "yes" else 0

    db = get_db()
    db.execute(
        "INSERT INTO rsvps (invite_code, name, attending, guests_count, allergies, note, created_at) VALUES (?,?,?,?,?,?,?)",
        (
            invite["code"],
            name,
            attending,
            guests_count,
            allergies,
            note,
            datetime.utcnow().isoformat(),
        ),
    )
    db.commit()

    # Volvemos a home con el mismo código y bandera "done"
    return render_template(
        "index.html",
        W=WEDDING,
        invite=invite,
        code=code,
        done=True,
        error=None,
    )


@bp.get("/calendar.ics")
def calendar_ics():
    """Archivo iCalendar para añadir la boda al calendario (Google/Apple)."""
    # Inicio: llegada de invitados
    dt_start = "20260912T194500"
    # Fin: 05:00 del día siguiente
    dt_end = "20260913T050000"

    title = f"Boda — {WEDDING['couple_full']}"
    location = f"{WEDDING['venue']} ({WEDDING['address']})"
    description = (
        f"{WEDDING['venue']}\n"
        f"{WEDDING['address']}\n\n"
        "Llegada 19:45 · Ceremonia 20:10 · Cóctel 20:40 · Cena 22:00 · Fiesta 00:00\n"
        "Recena 02:30 · Fin 05:00\n\n"
        f"Contacto: {WEDDING['contact_phone']}"
    )

    ics = "\r\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Cristhian & Diana//Boda//ES",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            f"UID:boda-{dt_start}@cristhian-diana",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            "DTSTART;TZID=Europe/Madrid:" + dt_start,
            "DTEND;TZID=Europe/Madrid:" + dt_end,
            "SUMMARY:" + title,
            "LOCATION:" + location.replace(",", "\\,"),
            "DESCRIPTION:" + description.replace("\n", "\\n").replace(",", "\\,"),
            "END:VEVENT",
            "END:VCALENDAR",
            "",
        ]
    )

    return Response(
        ics,
        mimetype="text/calendar; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=boda.ics"},
    )
