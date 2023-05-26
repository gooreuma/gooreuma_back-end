from datetime import datetime, timedelta

from sqlalchemy.exc import NoResultFound

from gooreuma.model.session import Session
from gooreuma.libs.database import db


class SessionController:
    def __init__(self):
        pass

    def create_session_key(self, user_email):
        # if session already exists, delete session
        session = Session.query.filter(Session.user_email == user_email)
        if db.session.query(session.exists()).scalar():
            session = Session.query.filter(Session.user_email == user_email).one()
            Session.query.filter(Session.session_key == session.session_key).delete()

        # create session
        session = Session(user_email=user_email)
        db.session.add(session)

        db.session.commit()
        cookie_data = {
            'session_key': session.session_key,
            'expired_at': datetime.strftime(session.expired_at, "%Y-%m-%d %H:%M:%S")
        }
        return cookie_data

    def delete_session(self, session_key):
        Session.query.filter(Session.session_key == session_key).delete()
        db.session.commit()
        return
