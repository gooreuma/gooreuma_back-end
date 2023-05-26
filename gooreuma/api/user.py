from gooreuma.blueprints import user
from gooreuma.controller.UserController import UserController
from urllib import parse

from flask import request, make_response, abort

from gooreuma.libs.decorator import session_authenticate
from gooreuma.model.user import User

userController = UserController()


@user.route('/login', methods=['POST'])
def login():
    cookie_data = userController.authenticate(request.get_json())
    response = make_response()

    # set cookie
    expired_at = cookie_data['expired_at']
    for key, value in cookie_data.items():
        response.set_cookie(key, parse.quote(value), domain='.gooreuma.cloud', expires=expired_at)
    return response


@user.route('/logout', methods=['POST'])
def logout():
    return userController.user_logout(request.cookies.get('session_key'))


@user.route('/email-check', methods=['POST'])
def email_check():
    return userController.check_email(request.get_json())


@user.route('/register', methods=['POST'])
def register():
    try:
        return userController.create_user(request.get_json())
    except:
        return abort(404)


@user.route('/list')
@session_authenticate
def list(**kwargs):
    return userController.get_user_list()
