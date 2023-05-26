from flask import jsonify

from gooreuma.controller.OpenStackController import OpenStackController

openstack_controller = OpenStackController()


class ImageController:
    def __init__(self):
        pass

    def get_image_list(self, email):
        conn = openstack_controller.create_admin_connection()
        images = conn.list_images()
        image_list = []
        for image in images:
            image_list.append(
                {
                    "id": image.id,
                    "image_name": image.name,
                    "size": str(round(image.size/(1024*1024), 2))+" MB",
                    "description": image.name
                }
            )

        return jsonify({"images": image_list})
