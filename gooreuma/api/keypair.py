from gooreuma.blueprints import keypair
from gooreuma.controller.KeypairController import KeypairController
from flask import request, abort, Response

from gooreuma.libs.decorator import session_authenticate

keypairController = KeypairController()


@keypair.route('/create', methods=['POST'])
@session_authenticate
def create_keypair(**kwargs):
    try:
        keypair = keypairController.create_keypair(request.get_json(), kwargs['email'])
        return keypair
    except:
        return abort(404)


@keypair.route('/list')
@session_authenticate
def keypair_list(**kwargs):
    return keypairController.keypair_list(kwargs['email'])


@keypair.route('/delete', methods=['POST'])
@session_authenticate
def delete_keypair(**kwargs):
    try:
        keypairController.delete_keypair(request.get_json(), kwargs['email'])
        return Response("", status=200, mimetype='application/json')
    except:
        return abort(404)
