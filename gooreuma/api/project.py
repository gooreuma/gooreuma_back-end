from gooreuma.blueprints import project
from gooreuma.controller.ProjectController import ProjectController
from flask import request, abort, Response

from gooreuma.libs.decorator import session_authenticate

projectController = ProjectController()


@project.route('/create', methods=['POST'])
@session_authenticate
def create_project(**kwargs):
    projectController.create_project(request.get_json(), kwargs['email'])
    return {"message": "success project creation"}


@project.route('/add-member', methods=['POST'])
@session_authenticate
def add_member_to_project(**kwargs):
    projectController.add_member_to_project(request.get_json())
    return {
        "message": "success add member into project"
    }


@project.route('/list')
@session_authenticate
def project_list(**kwargs):
    return projectController.project_list(kwargs['email'], kwargs['role'])


@project.route('/detail/<project_id>')
@session_authenticate
def project_detail(project_id, **kwargs):
    return projectController.project_detail(project_id, kwargs['email'], kwargs['role'])
