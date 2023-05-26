from gooreuma.libs.database import db


class Instance(db.Model):
    __tablename__ = 'instance'
    instance_id = db.Column(db.String(50), primary_key=True)
    domain = db.Column(db.Text(100))
    domain_id = db.Column(db.Text(100))
    port = db.Column(db.Integer)
    project_id = db.Column(db.String(50), db.ForeignKey("project.project_id"))

    __table_args__ = {'extend_existing': True}

    def __init__(self, instance_id, project_id, port):
        self.instance_id = instance_id
        self.project_id = project_id
        self.port = port

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}
