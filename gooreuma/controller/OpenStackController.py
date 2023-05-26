import os

import openstack
from gooreuma.model.user import User
from gooreuma.model.project import Project
from gooreuma.model.studentInProject import StudentInProject


class OpenStackController:
    def __init__(self):
        pass

    def create_admin_connection(self):
        admin = User.query.filter(User.email == 'admin').one()
        return openstack.connect(
            auth_url=os.environ['OPENSTACK_AUTH_URL'],
            username=admin.email,
            password=admin.password,
            project_id=os.environ['OPENSTACK_ADMIN_PROJECT'],
            project_name="admin",
            user_domain_name="Default",
            project_domain_name="default",
            region_name="RegionOne",
            interface="public",
            identity_api_version=3
        )

    def create_connection(self, email):
        # Find user and project for connection
        user = User.query.filter(User.email == email).one()
        project = Project.query.filter(Project.project_id == StudentInProject.query.filter(
            StudentInProject.student_email == email).all()[0].project_id).one()
        # return connection
        return openstack.connect(
            auth_url=os.environ['OPENSTACK_AUTH_URL'],
            username=user.email,
            password=user.password,
            project_id=project.project_id,
            project_name=project.project_name,
            user_domain_name="Default",
            project_domain_name="default",
            region_name="RegionOne",
            interface="public",
            identity_api_version=3
        )

    def create_connection_with_project_id(self, email, project_id):
        user = User.query.filter(User.email == email).one()
        project = Project.query.filter(Project.project_id == project_id).one()
        return openstack.connect(
            auth_url=os.environ['OPENSTACK_AUTH_URL'],
            username=user.email,
            password=user.password,
            project_id=project.project_id,
            project_name=project.project_name,
            user_domain_name="Default",
            project_domain_name="default",
            region_name="RegionOne",
            interface="public",
            identity_api_version=3
        )

    def create_connection_with_project_id_lower_version(self, email, project_id):
        user = User.query.filter(User.email == email).one()
        project = Project.query.filter(Project.project_id == project_id).one()
        return openstack.connect(
            auth_url=os.environ['OPENSTACK_AUTH_URL'],
            username=user.email,
            password=user.password,
            project_id=project.project_id,
            project_name=project.project_name,
            user_domain_name="Default",
            project_domain_name="default",
            region_name="RegionOne",
            interface="public",
            identity_api_version=3,
            compute_api_version=2.27
        )