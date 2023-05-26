import os
from glob import glob
from importlib import import_module
from importlib.util import find_spec as importlib_find
from flask_cors import CORS
from flask import Flask
from flask_migrate import Migrate

from gooreuma.blueprints import all_blueprints
from gooreuma.libs.database import db


migrate = Migrate()


def create_app():
    app = Flask(__name__)
    phase = os.getenv('SCHOOLOUD_ENV', 'dev/dev').lower()
    app.config.from_pyfile('../config/%s/config.cfg' % phase)

    # CORS
    cors = CORS(app, resources={r"/*": {
        "origins": "['http://localhost:3000', 'http://dev.schooloud.cloud', '*.gooreuma.cloud']",
        "allow_headers": "*",
        "expose_headers": "*"}}, supports_credentials=True)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    # blueprint
    for bp in all_blueprints:
        path_name = importlib_find(bp.import_name)
        import_module(path_name.name)
        app.register_blueprint(bp, url_prefix=bp.url_prefix)

    # import all models
    # model_path = importlib_find('model')
    # model_path = model_path.submodule_search_locations[0]
    # models = ['.'.join(('model', os.path.split(f)[-1][:-3]))for f in glob('{}/[!_]*.py'.format(model_path))]
    # for m in models:
    #     import_module(m)

    return app
