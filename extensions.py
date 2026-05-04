from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from flask_cors import CORS

db = SQLAlchemy()
swagger = Swagger()
cors = CORS()
