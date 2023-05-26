import datetime
import math

from sqlalchemy import desc, asc
from sqlalchemy.exc import NoResultFound
from gooreuma.libs.database import db

from gooreuma.model.project import Project

from gooreuma.controller.OpenStackController import OpenStackController
from gooreuma.model.proposal import Proposal
from gooreuma.model.studentInProject import StudentInProject
from flask import jsonify, abort
from gooreuma.model.user import User
from urllib import parse

openstack_controller = OpenStackController()


class ProjectController:
    def __init__(self):
        pass

    def get_project(self, project_id):
        project = Project.query.filter(Project.project_id == project_id).one()
        project_dict = {
            'is_deleted': project.is_deleted,
            'name': project.project_name,
            'cpu': project.cpu,
            'memory': project.memory,
            'storage': project.storage,
            'create_at': project.create_at,
            'end_at': project.end_at,
        }
        return project_dict

    # 제안서 승인 시 호출
    def create_project(self, params, email):
        # Get a proposal from relevant proposal
        proposal = Proposal.query.filter(Proposal.proposal_id == params['proposal_id']).one()
        # Create project on openstack
        conn = openstack_controller.create_admin_connection()
        created_project = conn.create_project(name=proposal.project_name, domain_id="default")
        # Get role and Add current user to created project
        user_id = conn.get_user(name_or_id=email).id
        role_id = conn.get_role(name_or_id="member").id
        conn.identity.assign_project_role_to_user(project=created_project.id, user=user_id, role=role_id)

        # Set quotas specified on proposal
        conn.set_compute_quotas(name_or_id=created_project.id, instances=proposal.cpu, ram=int(proposal.memory*1024), cores=proposal.cpu)
        conn.set_volume_quotas(name_or_id=created_project.id, gigabytes=proposal.storage)

        # Create project on backend server
        project = Project(
            project_id=created_project.id,
            project_name=proposal.project_name,
            is_deleted=False,
            cpu=proposal.cpu,
            memory=proposal.memory,
            storage=proposal.storage,
            create_at=datetime.datetime.now(),
            end_at=proposal.end_at
        )
        db.session.add(project)
        student_in_project = StudentInProject(
            student_email=email,
            project_id=project.project_id
        )
        db.session.add(student_in_project)
        db.session.commit()

        conn = openstack_controller.create_connection_with_project_id(email=email, project_id=project.project_id)

        # Create private network (with admin auth)
        private_net = conn.create_network(
            name="private"
        )

        # Update Security group Rule
        security_group = conn.get_security_group(name_or_id="default").id
        conn.create_security_group_rule(
            secgroup_name_or_id=security_group
        )

        # Create subnet for private network
        subnet = conn.create_subnet(
            network_name_or_id=private_net.id,
            subnet_name='private-subnet',
            cidr="10.0.100.0/24",
            allocation_pools=[{"start": "10.0.100.2", "end": "10.0.100.254"}],
            gateway_ip="10.0.100.1",
            enable_dhcp=True,
            dns_nameservers=['8.8.8.8', ]
        )

        # Create router to connect between public and private
        public_net = conn.get_network(
            name_or_id="public"
        )

        router = conn.create_router(
            name="public-private-router",
            ext_gateway_net_id=public_net.id
        )

        conn.add_router_interface(
            router=router.id,
            subnet_id=subnet.id
        )

        return project.project_id


    def add_member_to_project(self, params):
        project = params['project_id']
        member = params['email']

        # Get role, userid and Add member
        conn = openstack_controller.create_admin_connection()
        user_id = conn.get_user(name_or_id=member).id
        role = conn.get_role(name_or_id='member').id
        conn.identity.assign_project_role_to_user(project=project, user=user_id, role=role)

        # add member to student in project
        student_in_project = StudentInProject(
            student_email=member,
            project_id=project
        )
        db.session.add(student_in_project)
        db.session.commit()
        return student_in_project

    def project_list(self, email, role):
        ####### 출력부 리팩토링 필요 #######
        projects = []
        # Case #1 : Student project list
        if role == 'STUDENT':
            user_projects = (
                StudentInProject.query.join(Project, StudentInProject.project_id == Project.project_id)
                .add_columns(Project.project_name, Project.create_at)
                .filter(StudentInProject.student_email == email).order_by(asc(Project.create_at))
                .all()
            )

            for project in user_projects:
                projects.append(
                    {
                        "project_id": project[0].project_id,
                        "project_name": project.project_name
                    }
                )

        # Case #2 : Admin or Professor project list
        elif role == 'ADMIN' or role == 'PROFESSOR':
            user_projects = Project.query.order_by(asc(Project.create_at)).all()
            for project in user_projects:
                try:
                    member_count = (
                        len(StudentInProject.query.filter(StudentInProject.project_id == project.project_id).all())
                    )
                except NoResultFound:
                    member_count = 0

                projects.append(
                    {
                        "project_id": project.project_id,
                        "project_name": project.project_name,
                        "member_count": member_count
                    }
                )
        else:
            user_projects = []
        
        return jsonify({"projects": projects})

    def project_detail(self, project_id, email, role):
        # project에 연결된 email 이거나, role이 admin인 경우에만 동작
        # Get Project
        if role == "ADMIN":
            project = (
                StudentInProject.query.filter(StudentInProject.project_id == project_id)
                .join(Project, StudentInProject.project_id == Project.project_id)
                .add_columns(Project.project_name, Project.create_at, Project.cpu, Project.memory, Project.storage,
                             Project.end_at)
                .all()[0]
            )
            conn = openstack_controller.create_admin_connection()
            # instances = conn.list_servers(filters={"tenant_id": project_id})
            instance_list = conn.list_servers(all_projects=True)
            instances = []
            for instance in instance_list:
                if instance.location['project']['id'] == project_id:
                    instances.append(instance)
        else:
            project = (
                StudentInProject.query.filter(StudentInProject.student_email == email)
                .filter(StudentInProject.project_id == project_id)
                .join(Project, StudentInProject.project_id == Project.project_id)
                .add_columns(Project.project_name, Project.create_at, Project.cpu, Project.memory, Project.storage,
                             Project.end_at)
                .one()
            )
            conn = openstack_controller.create_connection_with_project_id(email, project_id)
            instances = conn.list_servers()

        # Get quota of a selected project
        compute_quota = conn.get_compute_quotas(name_or_id=project_id)
        volume_quota = conn.get_volume_quotas(name_or_id=project_id)
        cpu_limit = compute_quota.cores
        memory_limit = compute_quota.ram
        storage_limit = volume_quota.gigabytes
        cpu_usage = 0
        memory_usage = 0
        storage_usage = 0

        # Get all instances usage
        for instance in instances:
            cpu_usage += instance.flavor.vcpus
            memory_usage += instance.flavor.ram
            storage_usage += instance.flavor.disk

        # Get current instance number on openstack
        instance_num = len(instances)

        # Get members
        students = (
            StudentInProject.query.filter(StudentInProject.project_id == project_id)
            .join(User, StudentInProject.student_email == User.email)
            .add_columns(User.name)
            .all()
        )
        members = []

        for student in students:
            members.append(
                {
                    "name": student.name,
                    "email": student[0].student_email
                }
            )

        return {
            "name": project.project_name,
            "create_at": project.create_at,
            "instance_num": instance_num,
            "end_at": project.end_at,
            "members": members,
            "memory_usage": memory_usage / 1024,
            "memory_limit": memory_limit / 1024,
            "cpu_usage": cpu_usage,
            "cpu_limit": cpu_limit,
            "storage_usage": storage_usage,
            "storage_limit": storage_limit
        }
