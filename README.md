# GuideSync — Trekking Management System

GuideSync is an academic project (MAD-2). It is a 3-role web application for
managing treks: **Admin**, **Trek Staff**, and **User (Trekker)**.

- **Backend:** Flask + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-Caching (Redis) + Celery
- **Frontend:** Vue 3 + Vue Router + Pinia + Bootstrap 5 + Axios + Chart.js (vue-chartjs)
- **Database:** SQLite (created programmatically)
- **Email:** Mailhog (dev SMTP catcher) on port 1025 — UI at http://localhost:8025

---

## Login details (created by the seed script)

| Role    | Email                | Password |
|---------|----------------------|----------|
| Admin   | admin@gmail.com      | admin123 |
| Staff   | staff@gmail.com      | staff123 |
| Trekker | trekker@gmail.com    | trek123  |

New trekkers can also self-register on the Register page.

---

## How to run

The backend stack (API, Redis, Celery, Mailhog) runs in **WSL (Ubuntu)**; the
frontend runs in **Windows PowerShell**. You need a few terminals for the full
demo.

### 1. Backend API — WSL
```bash
cd backend
pip install -r requirements.txt
# If upgrading from an older build, delete the old DB first (schema changed):
#   rm -f instance/database.db database.db
python seed.py        # creates database.db + sample data (run once)
python app.py         # starts API on http://127.0.0.1:5000
```

### 2. Redis (caching + Celery broker) — WSL
```bash
sudo service redis-server start      # or: redis-server
redis-cli ping                       # should print PONG
```
The app still works **without** Redis — it just falls back to an in-memory cache.

### 3. Celery worker (background jobs) — WSL
```bash
cd backend
celery -A celery_app.celery worker --loglevel=info
```

### 4. Celery beat (scheduler for daily/monthly jobs) — WSL
```bash
cd backend
celery -A celery_app.celery beat --loglevel=info
```

### 5. Mailhog (dev email catcher) — WSL
Download the MailHog binary once, then run it:
```bash
~/MailHog                            # SMTP on :1025, web inbox on :8025
```
Reminders, the monthly report, and the CSV export are emailed via SMTP to
Mailhog on port **1025**; read them at http://localhost:8025. If Mailhog isn't
running the CSV export still writes to disk and stays downloadable. The SMTP
target is configurable via env vars (`MAIL_HOST`, `MAIL_PORT`, `MAIL_SENDER`) —
see [backend/config.py](backend/config.py).

### 6. Frontend — Windows PowerShell
```powershell
cd frontend
npm install
npm run dev           # opens http://localhost:5173
```

---

## Project structure

```
backend/
├── app.py              # Flask app factory + app start
├── config.py           # config (DB, JWT, Redis, Celery)
├── extensions.py       # db, jwt, cache objects
├── models.py           # User, StaffProfile, Trek, Booking + admin seed
├── seed.py             # creates tables + sample data
├── celery_app.py       # Celery setup + beat schedule
├── tasks.py            # reminders, monthly report, CSV export
├── requirements.txt
└── routes/
    ├── auth.py         # register / login / logout / me
    ├── utils.py        # role_required decorator
    ├── cache_service.py# small Redis cache helper
    ├── admin.py        # admin endpoints
    ├── tstaff.py       # trek-staff endpoints
    └── trekker.py      # trekker endpoints (booking, export)

frontend/
└── src/
    ├── main.js
    ├── App.vue
    ├── router/index.js         # routes + role guard
    ├── services/api.js         # axios instance (JWT header)
    ├── stores/auth.js          # Pinia auth store
    ├── components/NavBar.vue
    └── views/
        ├── Home.vue
        ├── auth/{Login,Register}.vue
        ├── admin/{AdminDashboard,AdminTreks,AdminStaff,AdminUsers,AdminBookings,AdminReports}.vue
        ├── staff/{StaffDashboard,StaffTrek}.vue
        └── trekker/{TrekkerDashboard,TrekkerTreks,TrekkerBookings,TrekkerProfile}.vue
```

---

## Features

**Admin:** dashboard counts, trek CRUD, create staff, assign staff to treks,
view all bookings, search, deactivate/blacklist users, analytics.

**Trek Staff:** dashboard of assigned treks, update slots, change trek status
(Open/Closed/Started/Completed), view participants.

**Trekker:** browse & filter open treks, book (no overbooking / no duplicates),
cancel (slot is returned), booking history, edit profile, export bookings to CSV.

**Analytics (Chart.js):** admin Reports page renders a bar chart (popular treks)
and a doughnut chart (booking status), redrawn reactively via `computed` props.

**Background jobs (Celery, timezone Asia/Kolkata):**
- Daily reminder for treks starting within 3 days (emailed via Mailhog)
- Monthly activity report for the admin (emailed via Mailhog)
- User-triggered CSV export of booking history (emailed as attachment + download)

**Caching (Redis):** admin dashboard counts use `@cache.cached()` (global) and
per-user booking history uses `@cache.memoize()` (isolated per profile, no data
bleed). Caches invalidate automatically on writes. Falls back to an in-memory
cache if Redis is unreachable.

**Soft deletes:** treks are soft-deleted (`is_deleted`) so historical bookings
stay intact for analytics; cascade relationships are configured on the models.

---

## Business rules enforced in the API
1. No overbooking (slots checked before booking).
2. Booking allowed only when the trek is **Open**.
3. No duplicate active booking for the same trek.
4. Only the assigned staff can manage a trek.
5. Only one Admin (seeded — no admin registration).
6. Blacklisted / deactivated users cannot log in.
7. Bookings are never deleted (full history kept).
8. Cancelling a booking restores the slot (and re-opens a full trek).
