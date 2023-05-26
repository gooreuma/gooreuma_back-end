from gooreuma.blueprints import flavor
from gooreuma.controller.FlavorController import FlavorController
from gooreuma.libs.decorator import session_authenticate
from flask import request

flavorController = FlavorController()


@flavor.route('/list')
@session_authenticate
def get_flavor_list(**kwargs):
    response = flavorController.get_flavor_list(kwargs['email'])
    return response
