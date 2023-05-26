from sqlalchemy.exc import NoResultFound

from gooreuma.controller.ProjectController import ProjectController
from gooreuma.model.proposal import Proposal
from gooreuma.libs.database import db
from gooreuma.model.user import User


class ProposalController:
    def __init__(self):
        pass

    def get_proposal(self, proposal_id):
        proposal = Proposal.query.filter(Proposal.proposal_id == proposal_id).one()
        return proposal.as_dict()

    def set_proposal(self, request_data):
        purpose = request_data['purpose']
        project_name = request_data['name']
        instance_num = request_data['instance_num']
        cpu = request_data['cpu']
        memory = request_data['memory']
        storage = request_data['storage']
        author_email = request_data['author_email']
        end_at = request_data['end_at']

        proposal = Proposal(purpose=purpose, project_name=project_name, instance_num=instance_num, cpu=cpu,
                            memory=memory, storage=storage, status="WAIT", author_email=author_email, end_at=end_at)
        db.session.add(proposal)
        db.session.commit()
        return proposal.proposal_id

    def delete_proposal(self, request_data, user_email):
        proposal_id = request_data['proposal_id']

        # delete proposal
        proposal = Proposal.query.filter(Proposal.proposal_id == proposal_id)
        if db.session.query(proposal.exists()).scalar():
            proposal = Proposal.query.filter(Proposal.proposal_id == proposal_id).one()

            if proposal.status != 'APPROVED' and proposal.author_email == user_email:
                Proposal.query.filter(Proposal.proposal_id == proposal_id).delete()
                db.session.commit()

        return ''

    def get_proposal_list(self, user_email, role):
        proposal_list = []

        if role == 'ADMIN':
            proposals = Proposal.query.all()
        elif role == 'STUDENT':
            proposals = Proposal.query.filter(Proposal.author_email == user_email).all()
        elif role == 'PROFESSOR':  # for professor
            proposals = Proposal.query.all()
        for proposal in proposals:
            proposal_list.append(proposal.as_dict())
        return proposal_list

    def update_proposal_state(self, request_data, role):
        # check user's role
        if role == 'STUDENT':
            return {
                "message": "Error: student can't approve proposal"
            }

        proposal_id = request_data['proposal_id']
        is_approved = request_data['is_approved']

        if is_approved:
            proposal = Proposal.query.filter(Proposal.proposal_id == proposal_id)
            proposal.update({"status": "APPROVED"})
            db.session.commit()
            author_email = Proposal.query.filter(Proposal.proposal_id == proposal_id).one().author_email

            # 프로젝트 생성 함수 호출
            projectController = ProjectController()
            project_id = projectController.create_project(request_data, author_email)
            return {
                "message": "proposal APPROVED",
                "proposal_id": proposal_id,
                "project_id": project_id
            }

        else:
            proposal = Proposal.query.filter(Proposal.proposal_id == proposal_id)
            proposal.update({"status": "REJECTED"})
        db.session.commit()
        return {
                "message": "proposal REJECTED",
                "proposal_id": proposal_id
            }
