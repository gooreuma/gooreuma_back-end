from gooreuma.blueprints import domain
from gooreuma.controller.DomainController import DomainController
from gooreuma.libs.decorator import session_authenticate
from flask import request

domainController = DomainController()


@domain.route('/assign', methods=['POST'])
@session_authenticate
def assign_domain(**kwargs):
    params = request.get_json()
    response = domainController.assign_domain(params, kwargs['email'])
    return response


@domain.route('/delete', methods=['POST'])
@session_authenticate
def delete_domain(**kwargs):
    params = request.get_json()
    response = domainController.delete_domain(params['instance_id'], params['project_id'])
    return response


@domain.route('/list')
@session_authenticate
def get_domain_list(**kwargs):
    response = domainController.get_domain_list(kwargs['role'])
    return response

