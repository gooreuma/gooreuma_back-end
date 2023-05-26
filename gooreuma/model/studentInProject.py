from gooreuma.libs.database import db


class StudentInProject(db.Model):
    __tablename__ = 'student_in_project'
    # id = db.Column(db.Integer, primary_key=True)
    student_email = db.Column(db.String(50), db.ForeignKey("user.email"))
    # students = db.relationship("User", back_populates="projects")
    #
    project_id = db.Column(db.String(32), db.ForeignKey("project.project_id"))
    # projects = db.relationship("Project", back_populates="students")  # many-to-one 관계의 참조 변수

    __table_args__ = (
        db.PrimaryKeyConstraint(student_email, project_id),
        {
            'extend_existing': True
        })
