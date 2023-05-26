from gooreuma.blueprints import hello
from gooreuma.controller.ProposalController import ProposalController


pc = ProposalController()

@hello.route('/say')
def say_hello_world():
    print(pc.get_proposal(1))
    # print(pc.get_proposal(2))
    # pc.set_proposal("test","projecttt", 2, 3, 4, 4, "WAIT", "asdf")
    return 'Hello World!'


