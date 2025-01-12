from app import create_app
from app import config


if __name__ == "__main__":
    print("Ejecutandose", config)
    app = create_app()
    app.run(host= config.HOST,
            port= config.PORT,
            debug= config.DEBUG)