from apscheduler.schedulers.background import BackgroundScheduler
from .views import notify_user


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(notify_user, 'interval', seconds=50)
    scheduler.start()