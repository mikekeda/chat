import json

from celery import Celery

from channels import Group

from .models import Profile

app = Celery('chat')


@app.task
def update_user_statuses():
    Group('users').send({
        'text': json.dumps(Profile.get_online_users())
    })
