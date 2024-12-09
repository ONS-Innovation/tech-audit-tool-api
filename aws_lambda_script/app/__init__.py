import os
from flask import Flask

from .extensions import api
from .resources import ns


# Function to read the version from the .version file
def get_version():
    """
    Retrieves the version of the application from a .version file located in the same directory.
    This function reads the .version file to get the current version of the application. If the
    .version file is not found, it returns a default version "0.1.0".
    Returns:
        str: The version of the application as a string.
    """

    # Path to the .version file in the 'app' directory
    version_file = os.path.join(os.path.dirname(__file__), ".version")
    try:
        with open(version_file, "r") as file:
            version = file.read().strip()
            return version
    except FileNotFoundError:
        # Handle the case where the .version file is not found
        return "0.1.0"  # Default version in case the file is missing


def create_app():
    """
    Create and configure the Flask application.

    This function initializes the Flask application, sets up the API with
    documentation, security, and versioning, and returns the configured app instance.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)

    authorizations = {
        "ID Token": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter your id token in the format **<id_token>**",
        }
    }

    # Get the version from the .version file
    version = get_version()

    api.__init__(
        app,
        doc="/",
        title="Tech Audit Tool API",
        version=version,  # Use the dynamically loaded version here
        authorizations=authorizations,
        security="ID Token",
        description="""An API that saves and accesses data from an S3 bucket in AWS saved and queried as JSON.
                 Each route with /api/v1/ must use an Authorization header with a valid Cognito ID token.""",
    )
    api.add_namespace(ns)

    return app
