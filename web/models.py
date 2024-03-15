import time
from flask_login import UserMixin

from web import db, manager


class Tasks (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    started_at = db.Column(db.DateTime)
    stopped_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "task_id": self.id,
            "text": self.text,
            "started_at": int(time.mktime(self.started_at.timetuple()))*1000 if self.started_at else None,
            "stopped_at": int(time.mktime(self.stopped_at.timetuple()))*1000 if self.stopped_at else None,
            "is_active": self.is_active
        }



class Users (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)