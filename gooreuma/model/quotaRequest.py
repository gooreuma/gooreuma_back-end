import datetime

from gooreuma.libs.database import db


class QuotaRequest(db.Model):
    __tablename__ = 'quota_request'
    quota_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # author = db.relationship('User', backref=db.backref('quotaRequests'))
    author = db.Column(db.String(50), db.ForeignKey('user.email', ondelete='CASCADE'))

    purpose = db.Column(db.Text(200), nullable=False)
    memory = db.Column(db.Double, nullable=False)
    cpu = db.Column(db.Integer, nullable=False)
    storage = db.Column(db.Integer, nullable=False)
    create_at = db.Column(db.DateTime(), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    project_id = db.Column(db.String(32), db.ForeignKey("project.project_id"))
    # project = db.relationship("Project", back_populates="quotaRequests")  # many-to-one 관계의 참조 변수

    __table_args__ = {'extend_existing': True}

    def __init__(self, author, purpose, memory, cpu, storage, status, project_id):
        self.author = author
        self.purpose = purpose
        self.memory = memory
        self.cpu = cpu
        self.storage = storage
        self.create_at = datetime.datetime.now()
        self.status = status
        self.project_id = project_id

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}
