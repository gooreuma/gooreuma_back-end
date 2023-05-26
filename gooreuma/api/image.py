from gooreuma.blueprints import image
from gooreuma.controller.ImageController import ImageController
from flask import request, abort, Response

from gooreuma.libs.decorator import session_authenticate

imageController = ImageController()


@image.route('/list')
@session_authenticate
def image_list(**kwargs):
    try:
        images = imageController.get_image_list(kwargs['email'])
        return images
    except:
        return abort(404)
