from flask import Flask

UPLOAD_FOLDER = '../smpkelas/uploads'

app = Flask(__name__)
app.secret_key = 'SkripsiIsTheBest'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024