from gooreuma.libs.database import db
from datetime import datetime


class Proposal(db.Model):
    __tablename__ = 'proposal'
    proposal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    purpose = db.Column(db.Text(200), nullable=False)
    project_name = db.Column(db.String(30), nullable=False)
    create_at = db.Column(db.DateTime())
    instance_num = db.Column(db.Integer, nullable=False)
    cpu = db.Column(db.Integer, nullable=False)
    memory = db.Column(db.Double, nullable=False)
    storage = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    end_at = db.Column(db.DateTime())
    author_email = db.Column(db.String(50), db.ForeignKey('user.email'))

    __table_args__ = {'extend_existing': True}

    def __init__(self, purpose, project_name, instance_num, cpu, memory, storage, status, author_email, end_at):
        self.purpose = purpose
        self.project_name = project_name
        self.instance_num = instance_num
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
        self.status = status
        self.author_email = author_email
        self.create_at = datetime.now()
        self.end_at = datetime.strptime(end_at, "%Y-%m-%d")

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}
