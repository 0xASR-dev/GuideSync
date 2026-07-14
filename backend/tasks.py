import os
import csv
import smtplib
from email.message import EmailMessage
from datetime import date, datetime, timedelta
from flask import current_app
from celery_app import celery
from models import Trek, Booking, User


# ==========================================================================
# EMAIL HELPER  (delivers to Mailhog on localhost:1025)
# Mailhog is a dev SMTP catcher; view captured mail at http://localhost:8025
# ==========================================================================
def send_email(to_address, subject, html_body, attachment=None):
    msg = EmailMessage()
    msg['From'] = current_app.config['MAIL_SENDER']
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.set_content('This email requires an HTML-capable client.')
    msg.add_alternative(html_body, subtype='html')

    # attachment = (filename, bytes) tuple, e.g. the CSV export
    if attachment:
        filename, data = attachment
        msg.add_attachment(data, maintype='text', subtype='csv', filename=filename)

    host = current_app.config['MAIL_HOST']
    port = current_app.config['MAIL_PORT']
    with smtplib.SMTP(host, port) as smtp:
        smtp.send_message(msg)


# ==========================================================================
# 1) DAILY REMINDER  (scheduled by Celery Beat)
# For every trek starting within the next 3 days, remind each booked user.
# Here we just print the message (an email/webhook would go in the same spot).
# ==========================================================================
@celery.task
def send_daily_reminders():
    today = date.today()
    soon = today + timedelta(days=3)
    sent = 0

    for trek in Trek.query.filter_by(status='Open', is_deleted=False).all():
        if not trek.start_date:
            continue
        start = trek.start_date.date()

        if today <= start <= soon:
            bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
            for b in bookings:
                user = User.query.get(b.user_id)
                if user:
                    html = (
                        f'<h3>Trek reminder</h3>'
                        f'<p>Hi {user.full_name}, your trek '
                        f'<b>{trek.name}</b> starts on '
                        f'{start.strftime("%Y-%m-%d")} at {trek.location}.</p>'
                        f'<p>Get ready! — GuideSync</p>'
                    )
                    send_email(user.email, f'Reminder: {trek.name} starts soon', html)
                    sent += 1

    return f'Sent {sent} reminders'


# ==========================================================================
# 2) MONTHLY ADMIN REPORT  (scheduled by Celery Beat, 1st of month)
# Builds a small HTML summary of last month and "emails" it to the admin.
# ==========================================================================
@celery.task
def generate_monthly_report():
    completed = Trek.query.filter_by(status='Completed', is_deleted=False).count()
    total_bookings = Booking.query.count()
    total_trekkers = User.query.filter_by(role='trekker', is_deleted=False).count()

    # most popular treks by number of bookings
    treks = Trek.query.filter_by(is_deleted=False).all()
    popularity = []
    for t in treks:
        popularity.append((t.name, Booking.query.filter_by(trek_id=t.id).count()))
    popularity.sort(key=lambda x: x[1], reverse=True)
    top = popularity[:3]

    rows = ''.join(f'<li>{name}: {count} bookings</li>' for name, count in top)
    html = f"""
    <h2>GuideSync Monthly Report</h2>
    <p>Completed treks: {completed}</p>
    <p>Total bookings: {total_bookings}</p>
    <p>Total trekkers: {total_trekkers}</p>
    <h3>Top treks</h3>
    <ul>{rows or '<li>No bookings yet</li>'}</ul>
    """

    admin = User.query.filter_by(role='admin').first()
    if admin:
        send_email(admin.email, 'GuideSync Monthly Report', html)
    return 'Monthly report generated'


# ==========================================================================
# 3) USER CSV EXPORT  (triggered by the trekker from the UI)
# Writes the user's booking history to exports/<task_id>.csv
# ==========================================================================
@celery.task(bind=True)
def export_bookings_csv(self, user_id):
    folder = current_app.config['EXPORT_FOLDER']
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f'{self.request.id}.csv')

    def _d(value):
        return value.strftime('%Y-%m-%d') if isinstance(value, datetime) else (value or '')

    bookings = Booking.query.filter_by(user_id=user_id).all()

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'user_id', 'trek_name', 'location', 'booking_status',
            'booking_date', 'start_date', 'end_date',
        ])
        for b in bookings:
            trek = Trek.query.get(b.trek_id)
            writer.writerow([
                user_id,
                trek.name if trek else '',
                trek.location if trek else '',
                b.status,
                b.booking_date.strftime('%Y-%m-%d') if b.booking_date else '',
                _d(trek.start_date) if trek else '',
                _d(trek.end_date) if trek else '',
            ])

    # Also email the CSV to the trekker via Mailhog.
    # Kept non-fatal: if Mailhog isn't running the file is still on disk
    # and remains downloadable from the UI.
    user = User.query.get(user_id)
    if user:
        try:
            with open(path, 'rb') as f:
                data = f.read()
            html = (
                f'<h3>Your booking history</h3>'
                f'<p>Hi {user.full_name}, your requested CSV export is attached.</p>'
                f'<p>— GuideSync</p>'
            )
            send_email(user.email, 'Your GuideSync booking export',
                       html, attachment=('my_bookings.csv', data))
        except OSError as exc:
            print(f'[EXPORT] email skipped (mail server down?): {exc}')

    return path
