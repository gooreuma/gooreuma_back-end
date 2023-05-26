import openstack
from sqlalchemy.exc import NoResultFound

from gooreuma.model.user import User

from gooreuma.libs.database import db

from flask import jsonify, Response, abort

from gooreuma.controller.SessionController import SessionController
from gooreuma.controller.OpenStackController import OpenStackController

from openstack.identity.v3.user import User as KeystoneUser

openstack_controller = OpenStackController()
sessionController = SessionController()

class UserController:
    def __init__(self):
        pass

    # 유저 반환
    def get_user(self, email):
        user = User.query.filter(User.email == email).one()
        user_dict = {
            'student_id': user.studentd_id,
            'name': user.name,
            'password': user.password,
            'major': user.major,
            'role': user.role
        }
        return user_dict

    # 로그인
    def authenticate(self, params):
        try:
            user = User.query.filter(User.email == params['email']).one()
            if user.password != params['password']:
                return abort(404)
            else:
                # Cookie creation
                cookie_data = sessionController.create_session_key(user.email)
                cookie_data['email'] = user.email
                cookie_data['name'] = user.name
                cookie_data['role'] = user.role
                return cookie_data
        except NoResultFound:
            return abort(404)

    # 회원가입
    def create_user(self, params):
        # Save new user on Back-end DB
        user = User(
            email=params['email'],
            student_id=params['student_id'],
            name=params['name'],
            password=params['password'],
            major=params['major'],
            role=params['role']
        )
        db.session.add(user)
        db.session.commit()

        # Save new user on OpenStack keystone db
        conn = openstack_controller.create_admin_connection()
        keystone_user = KeystoneUser(
            name=user.name,
            password=user.password,
            domain_id="default"
        )
        conn.create_user(
            name=user.email,
            password=user.password,
            domain_id="default"
        )

        return Response("", status=200, mimetype="application/json")

    # 이메일 중복 체크
    def check_email(self, params):
        try:
            user = User.query.filter(User.email == params['email']).one()
            return abort(404)
        except NoResultFound:
            return Response("",status=200,mimetype='application/json')

    # 유저 전체 목록
    def get_user_list(self):
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                "email":user.email,
                "name":user.name,
                "major":user.major,
                "student_id":user.student_id,
                "role":user.role
            })
        return jsonify({"users":user_list})

    def user_logout(self, session_key):
        sessionController.delete_session(session_key)
        return ''
