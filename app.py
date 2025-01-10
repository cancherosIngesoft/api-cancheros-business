from flask import Flask
import os
from config import Config
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

# declaring flask application
app = Flask(__name__)

# calling the dev configuration
config = Config().dev_config

# making our application to use dev env
app.env = config.ENV

@app.route("/")
def hello_world():
    return "Hello, World!"
 
if __name__ == "__main__":
    app.run(host= config.HOST,
            port= config.PORT,
            debug= config.DEBUG)