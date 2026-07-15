from celery import Celery, Task
from celery.schedules import crontab
from app import create_app


flask_app = create_app()


def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config['CELERY'])
    celery_app.set_default()
    app.extensions['celery'] = celery_app
    return celery_app


celery = celery_init_app(flask_app)


celery.conf.timezone = 'Asia/Kolkata'
celery.conf.enable_utc = False

import tasks  

celery.conf.beat_schedule = {
    'daily-trek-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=7, minute=0),          # everyday 07:00
    },
    'monthly-admin-report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(hour=8, minute=0, day_of_month=1),  # 1 day of month
    },
}
