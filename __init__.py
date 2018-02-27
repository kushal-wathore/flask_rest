"""
The flask application package.
"""
import sys
sys.path.append('../')
from flask import Flask, request
app = Flask(__name__)

from flask_rest.views import *
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

