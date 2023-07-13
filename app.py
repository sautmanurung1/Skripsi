from flask import Flask


app = Flask(__name__)
app.secret_key = 'SkripsiIsTheBest'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024