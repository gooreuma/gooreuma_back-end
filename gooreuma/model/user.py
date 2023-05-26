from gooreuma.libs.database import db


class User(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String(50), primary_key=True)
    student_id = db.Column(db.String(20))
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    major = db.Column(db.String(30))
    role = db.Column(db.String(20), nullable=False)

    # proposals = db.relationship('gooreuma.model.proposal.Proposal', backref="author")

    # session = db.relationship("Session", back_populates="user", uselist=False)
    # quataRequests = db.relationship("QuataRequest", back_populates="author")
    # projects = db.relationship("StudentInProject", back_populates="students")

    __table_args__ = {'extend_existing': True}
