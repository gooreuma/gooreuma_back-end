from functools import wraps
from flask import request
from gooreuma.libs.database import db
from gooreuma.model.user import User
from datetime import datetime
from gooreuma.model.session import Session
from sqlalchemy.exc import NoResultFound


def session_authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            session_key = request.cookies.get('session_key')
            session = Session.query.filter(Session.session_key == session_key).one()
            if datetime.now() > session.expired_at:
                return {"message": "session expired"}, 401

            # get user information from session database
            user = User.query.filter(User.email == session.user_email).one()
            kwargs['email'] = session.user_email
            kwargs['role'] = user.role
            kwargs['name'] = user.name
        except NoResultFound:
            return {"message": "invalid session"}, 401
        return f(*args, **kwargs)

    return decorated_function
