# Web RSVP Boda — Cristhian & Diana (Flask)

Web RSVP en **Python + Flask** lista para ejecutar en VS Code.
Incluye:
- Página principal con detalles y formulario RSVP
- Códigos por invitación (QR único) con **límite de asistentes** por familia
- Panel **/admin** (usuario/contraseña) para ver respuestas y exportar CSV

## 1) Requisitos
- Python 3.11+ recomendado

## 2) Arranque rápido (VS Code)
1. Abre esta carpeta en VS Code.
2. Crea el entorno virtual:
   - Windows: `python -m venv .venv`
   - Mac/Linux: `python3 -m venv .venv`
3. Activa el entorno:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Instala dependencias:
   - `pip install -r requirements.txt`
5. Configura variables:
   - Copia `.env.example` a `.env` y edita `SECRET_KEY`, `ADMIN_USER`, `ADMIN_PASS`
6. Ejecuta:
   - `python run.py`
7. Abre:
   - http://127.0.0.1:5000

## 3) QR general vs QR único (resumen)
- **QR general:** todos entran a la misma URL. Es lo más simple, pero no limita asistentes por invitación.
- **QR único:** cada invitación lleva una URL con `?code=XXXX`. Cada `code` tiene `max_guests` (ej. 2, 5, etc.).

En este proyecto usamos **QR único** (lo que necesitas para familias de 2/5/etc.).

## 4) Crear códigos por invitación
Entra a `/admin` (con tu usuario/contraseña) → "Invitaciones" → crea códigos.
- `code`: texto corto (ej. `FAMGARCIA5`)
- `label`: referencia (ej. "Familia García")
- `max_guests`: 5

Luego el QR debe apuntar a:
- `https://tu-dominio.com/?code=FAMGARCIA5`

## 5) Exportar RSVPs
En `/admin` hay botón "Exportar CSV".

## 5.1) Añadir vuestras fotos (la “magia”)
La web incluye placeholders en `app/static/img/`:
- `foto_1.svg`, `foto_2.svg`, `foto_3.svg`

Para usar fotos reales:
1. Copia vuestros JPG/PNG en `app/static/img/` con estos nombres:
   - `foto_1.jpg`, `foto_2.jpg`, `foto_3.jpg`
2. Abre `app/templates/index.html` y cambia las rutas donde pone `foto_*.svg` por `foto_*.jpg`.

Tip: fotos horizontales quedan perfectas (se recortan con `object-fit: cover`).

## 6) Base de datos
Se crea automáticamente como `instance/rsvp.sqlite`.

---
Hecho con cariño y con foco en estética editorial (no cursi).
