from flask import Flask
from flask_cors import CORS

#app.config['CORS_HEADERS'] = 'Content-Type'


app = Flask(__name__,template_folder='templates')#,static_url_path='static')
app.static_url_path = 'static'
cors = CORS(app, resources={r"/*": {"origins": "*"}})

from app import routes