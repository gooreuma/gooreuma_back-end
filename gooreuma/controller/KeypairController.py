from gooreuma.controller.OpenStackController import OpenStackController

from flask import jsonify

openstack_controller = OpenStackController()


class KeypairController:
    def __init__(self):
        pass

    def create_keypair(self, body_params, email):
        # Create keypair
        conn = openstack_controller.create_connection(email)
        private_key = conn.create_keypair(body_params['keypair_name'])

        return jsonify({"private_key": private_key.private_key})

    def keypair_list(self, email):
        conn = openstack_controller.create_connection(email)
        keys = conn.list_keypairs()
        key_list = []

        for key in keys:
            key_list.append({
                "keypair_name": key.name,
                "finger_print": key.fingerprint,
                "public_key": key.public_key
            })

        return jsonify({"key_list": key_list})

    def delete_keypair(self, params, email):
        conn = openstack_controller.create_connection(email)
        conn.delete_keypair(params["keypair_name"])
