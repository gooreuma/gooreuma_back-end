from gooreuma import create_app


app = create_app()


if __name__ == '__main__':
    config = app.config
    app.run(config['HOST'], config['PORT'], threaded=config['THREADED'])
