from flask import jsonify, request, Response

from gooreuma.model.quotaRequest import QuotaRequest
from gooreuma.model.project import Project
from gooreuma.controller.OpenStackController import OpenStackController
from gooreuma.controller.ProjectController import ProjectController
from gooreuma.libs.database import db

openstackController = OpenStackController()
projectController = ProjectController()

class QuotaController:
    def __init__(self):
        pass

    def get_quota_request(self, quota_request_id):
        quota_request = QuotaRequest.query.filter(QuotaRequest.quota_request_id == quota_request_id).one()
        quota_request_dict = {
            'author': quota_request.author,
            'purpose': quota_request.purpose,
            'memory': quota_request.memory,
            'v_cpu': quota_request.cpu,
            'storage': quota_request.storage,
            'create_at': quota_request.create_at,
            'status': quota_request.status,
            'project_id': quota_request.project_id
        }
        return quota_request_dict

    def current_usage(self, role):
        # Quota values
        cpu_limit = 0
        memory_limit = 0
        storage_limit = 0
        # Instance usage values
        cpu_usage = 0
        memory_usage = 0
        storage_usage = 0
        # User count initial value
        user_count = 0
        # Case #1 : Admin Get all projects quota
        if role == 'ADMIN' or role == 'PROFESSOR':
            # Get all quotas
            conn = openstackController.create_admin_connection()
            all_projects = conn.list_projects()
            for project in all_projects:
                compute_quota = conn.get_compute_quotas(name_or_id=project.id)
                volume_quota = conn.get_volume_quotas(name_or_id=project.id)
                cpu_limit += compute_quota.cores
                memory_limit += compute_quota.ram
                storage_limit += volume_quota.gigabytes
            # Get all instances usage
            all_instances = conn.compute.servers(all_projects=True)
            for instance in all_instances:
                cpu_usage += instance.flavor.vcpus
                memory_usage += instance.flavor.ram
                storage_usage += instance.flavor.disk
            # Get User count
            user_count = len(conn.list_users())

        return jsonify({
            "memory_usage": memory_usage / 1024,
            "memory_limit": memory_limit / 1024,
            "cpu_usage": cpu_usage,
            "cpu_limit": cpu_limit,
            "storage_usage": storage_usage,
            "storage_limit": storage_limit,
            "user_count": user_count
        })

    def create_request(self, params, email):
        project_id = params['project_id']
        purpose = params['purpose']
        memory = params['memory']
        cpu = params['cpu']
        storage = params['storage']

        quota_request = QuotaRequest(
            author=email,
            purpose=purpose,
            memory=memory,
            cpu=cpu,
            storage=storage,
            status="WAIT",
            project_id=project_id
        )

        db.session.add(quota_request)
        db.session.commit()

        return jsonify({"message": "request sending complete"})

    def update_quota_request_state(self, params, role):
        if role == 'STUDENT':
            return {
                "message": "invalid access"
            }
        quota_request_id = params['quota_request_id']
        is_approved = params['approval']
        quota_request = QuotaRequest.query.filter(QuotaRequest.quota_request_id == quota_request_id)

        if is_approved:
            quota_request.update({"status": "APPROVED"})
            quota_request = QuotaRequest.query.filter(QuotaRequest.quota_request_id == quota_request_id).one()
            project_id = quota_request.project_id
            cpu = quota_request.cpu
            memory = quota_request.memory
            storage = quota_request.storage
            # Set quota changes
            conn = openstackController.create_admin_connection()
            conn.set_compute_quotas(name_or_id=project_id, cores=cpu,
                                    ram=int(memory * 1024))
            conn.set_volume_quotas(name_or_id=project_id, gigabytes=storage)

            # Update project information
            project = Project.query.filter(Project.project_id == project_id)
            project.update({'cpu': cpu, 'memory': memory, 'storage': storage})

            db.session.commit()

            return jsonify({
                "message": "quota_request APPROVED",
                "quota_request_id": quota_request_id
            })

        else:
            quota_request.update({"status": "REJECTED"})
            db.session.commit()

            return jsonify({
                "message": "quota_request REJECTED",
                "quota_request_id": quota_request_id
            })

    def get_quota_request_list(self, role, email):
        return_list = []
        quota_request_list = []

        if role == 'ADMIN':
            quota_request_list = QuotaRequest.query.all()
        elif role == 'STUDENT':
            quota_request_list = QuotaRequest.query.filter(QuotaRequest.author == email).all()

        for quota_request in quota_request_list:
            project = Project.query.filter(Project.project_id == quota_request.project_id).one()

            quota_request_dict = quota_request.as_dict()
            quota_request_dict['project_name'] = project.project_name
            return_list.append(quota_request_dict)
        return {
            "quota_requests": return_list
        }

    def get_quota_request(self, quota_request_id, email, role):
        quota_request = QuotaRequest.query.filter(QuotaRequest.quota_request_id == quota_request_id).one()
        project_id = quota_request.project_id

        quota_request_dict = quota_request.as_dict()
        quota_request_dict['project_detail'] = projectController.project_detail(project_id, email, role)
        return jsonify(quota_request_dict)
