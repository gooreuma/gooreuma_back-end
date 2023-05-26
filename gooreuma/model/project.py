from gooreuma.libs.database import db


class Project(db.Model):
    __tablename__ = 'project'
    project_id = db.Column(db.String(32), primary_key=True)
    is_deleted = db.Column(db.Boolean, nullable=False)
    project_name = db.Column(db.String(30), nullable=False)
    cpu = db.Column(db.Integer, nullable=False)
    memory = db.Column(db.Double, nullable=False)
    storage = db.Column(db.Integer, nullable=False)
    create_at = db.Column(db.DateTime(), nullable=False)
    end_at = db.Column(db.DateTime(), nullable=False)

    # instances = db.relationship("Instance", back_populates="project")
    # quataRequests = db.relationship("QuataRequest", back_populates="project")
    # students = db.relationship("StudentInProject", back_populates="projects")

    __table_args__ = {'extend_existing': True}