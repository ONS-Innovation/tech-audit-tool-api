import pytest
from flask import Flask
from flask_restx import Api
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../aws_lambda_script')))

# Import your Flask app/namespace from aws_lambda_script/app
from app import ns  # Assuming ns is the namespace for your API



@pytest.fixture
def client():
    app = Flask(__name__)  # Initialize Flask app
    api = Api(app)  # Create the Api object
    api.add_namespace(ns)  # Register the Namespace with the Api

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
