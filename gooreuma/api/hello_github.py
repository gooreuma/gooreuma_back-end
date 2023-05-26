from gooreuma.blueprints import hello_github


@hello_github.route('/say')
def say_hello_github():
    return 'Hello Github!'


