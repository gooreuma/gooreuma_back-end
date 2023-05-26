from gooreuma.libs.database import db
from datetime import datetime, timedelta
import secrets


class Session(db.Model):
    __tablename__ = 'session'
    session_key = db.Column(db.String(32), primary_key=True)
    expired_at = db.Column(db.DateTime(), nullable=False)
    user_email = db.Column(db.String(50), db.ForeignKey("user.email"))

    __table_args__ = {'extend_existing': True}

    def __init__(self, user_email):
        self.session_key = secrets.token_hex(16)
        self.user_email = user_email
        self.expired_at = datetime.now() + timedelta(days=1)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}
