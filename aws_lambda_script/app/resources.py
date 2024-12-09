import logging
import os
from http import HTTPStatus
import requests
from flask_restx import Resource, Namespace, reqparse, abort
from .api_models import get_project_model, get_refresh_model
from .utils import (
    read_data,
    write_data,
    read_array_data,
    write_array_data,
    verify_cognito_token,
    cognito_data,
)

# Set namespace as /api/ - each request has to be <url>/api/v1/<endpoint>
ns = Namespace("v1", path="/api/v1/", description="")

project_model = get_project_model()
refresh_model = get_refresh_model()

# Create required authorization header
parser = reqparse.RequestParser()
parser.add_argument(
    "Authorization",
    location="headers",
    required=True,
    help="Authorization header is required",
)

required_param = {"Authorization": "ID Token required"}

# Set logger for AWS cloudwatch to return just errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Function to get the user email from the token
def get_user_email(args):
    token = args["Authorization"]
    try:
        user_attributes = verify_cognito_token(token)
        owner_email = user_attributes["email"]
        if not owner_email:
            logger.error("No email found in user attributes")
            abort(401, description="Not authorized")
        return owner_email
    except Exception as error:
        logger.exception("Error verifying token: %s", error)
        abort(401, description="Not authorized")


# Route to return the user email from the token in authorization header
@ns.route("/user")
class User(Resource):
    @ns.doc(responses={200: "Success", 401: "Authorization is required"})
    def get(self):
        owner_email = get_user_email(parser.parse_args())
        return {"email": owner_email}, 200


# Route to return all projects with optional filters
filterParser = reqparse.RequestParser()
filterParser.add_argument(
    "email",
    location="args",
    action="split",
    required=False,
    help="User email to filter by",
)
filterParser.add_argument(
    "roles", location="args", action="split", required=False, help="Roles to filter by"
)
filterParser.add_argument(
    "name",
    location="args",
    action="split",
    required=False,
    help="Project name to filter by",
)
filterParser.add_argument(
    "developed",
    location="args",
    action="split",
    required=False,
    help="Developed partners to filter by",
)
filterParser.add_argument(
    "languages",
    location="args",
    action="split",
    required=False,
    help="Languages to filter by",
)
filterParser.add_argument(
    "source_control",
    location="args",
    action="split",
    required=False,
    help="Source control to filter by",
)
filterParser.add_argument(
    "hosting",
    location="args",
    action="split",
    required=False,
    help="Hosting type to filter by",
)
filterParser.add_argument(
    "database",
    location="args",
    action="split",
    required=False,
    help="Database to filter by",
)
filterParser.add_argument(
    "frameworks",
    location="args",
    action="split",
    required=False,
    help="Frameworks to filter by",
)
filterParser.add_argument(
    "cicd",
    location="args",
    action="split",
    required=False,
    help="CI/CD tools to filter by",
)
filterParser.add_argument(
    "infrastructure",
    location="args",
    action="split",
    required=False,
    help="Infrastructure to filter by",
)
filterParser.add_argument(
    "return",
    location="args",
    action="split",
    required=False,
    help="Sections to return: user, details, developed, source_control, architecture, or whole project",
)

filter_params_docs = {
    "email": "User email to filter by",
    "roles": "Roles to filter by",
    "name": "Project name to filter by",
    "developed": 'Developed partners or "In house, partnership or outsourced" to filter by',
    "languages": "Languages to filter by",
    "source_control": "Source control to filter by",
    "hosting": "Hosting type to filter by",
    "database": "Database to filter by",
    "frameworks": "Frameworks to filter by",
    "cicd": "CI/CD tools to filter by",
    "infrastructure": "Infrastructure to filter by",
    "return": "Sections to return: user, details, developed, source_control, architecture, or whole project",
}


def flatten(nested_list):
    """Flatten a nested list structure without using additional imports."""
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list


def build_project_response(project, sections_to_return):
    """Build partial project data based on sections specified in return parameter."""
    partial_project = {}
    section_map = {
        "user": "user",
        "details": "details",
        "developed": "developed",
        "source_control": "source_control",
        "architecture": "architecture",
    }
    for section in sections_to_return:
        if section.lower() in section_map:
            partial_project[section_map[section.lower()]] = project[
                section_map[section.lower()]
            ]
    return partial_project or project


def get_nested_values(data, path):
    """Extract values from nested dictionary/list following the given path."""
    result = [data]
    for key in path:
        temp = []
        for item in result:
            if isinstance(item, dict):
                # Make dictionary key lookup case-insensitive
                value = None
                for k in item:
                    if k.lower() == key.lower():
                        value = item[k]
                        break
                if value is None:
                    value = []
                # Special handling for "main" and "others" arrays
                if isinstance(value, dict) and "main" in value and "others" in value:
                    temp.extend(value["main"])
                    temp.extend(value["others"])
                else:
                    temp.extend([value] if not isinstance(value, list) else value)
            elif isinstance(item, list):
                temp.extend(
                    flatten(
                        [i.get(key, []) if isinstance(i, dict) else i for i in item]
                    )
                )
        result = temp
    return [str(val).lower() for val in flatten(result)]


def matches_filter(data_values, filter_values):
    """Check if any filter value matches any data value."""
    return any(
        any(filter_val.lower() == val for val in data_values)
        for filter_val in filter_values
    )


# Main get function
@ns.route("/projects/filter")
class Filter(Resource):
    @ns.doc(
        params=filter_params_docs,
        responses={200: "Success", 401: "Authorization is required"},
    )
    def get(self):
        get_user_email(parser.parse_args())
        args = filterParser.parse_args()
        filter_params = {k: v for k, v in args.items() if k and v}

        data = read_data()
        projects = data["projects"]

        # Define paths for different filter types
        paths = {
            "email": ["user", "email"],
            "roles": ["user", "roles"],
            "name": ["details", "name"],
            "languages": ["architecture", "languages"],
            "hosting": ["architecture", "hosting"],
            "database": ["architecture", "database"],
            "frameworks": ["architecture", "frameworks"],
            "cicd": ["architecture", "CICD"],
            "infrastructure": ["architecture", "infrastructure"],
        }

        # Special case filters
        def filter_developed(project):
            if "developed" not in filter_params:
                return True
            project_type = project["developed"][0].lower()
            partners = [p.lower() for p in (project["developed"][1] or [])]
            return any(
                f.lower() == project_type or any(f.lower() in p for p in partners)
                for f in filter_params["developed"]
            )

        def filter_source_control(project):
            if "source_control" not in filter_params:
                return True
            return all(
                any(
                    f.lower() in sc["type"].lower()
                    or any(
                        f.lower() in link["description"].lower()
                        or f.lower() in link["url"].lower()
                        for link in sc["links"]
                    )
                    for sc in project["source_control"]
                )
                for f in filter_params["source_control"]
            )

        # Filter projects
        filtered_projects = []
        for project in projects:
            # Apply standard filters
            standard_filters_pass = all(
                matches_filter(
                    get_nested_values(project, paths[key]), filter_params[key]
                )
                for key in filter_params
                if key in paths
            )

            # Apply special case filters
            if (
                standard_filters_pass
                and filter_developed(project)
                and filter_source_control(project)
            ):

                # Handle return parameter
                if "return" in filter_params:
                    filtered_projects.append(
                        build_project_response(project, filter_params["return"])
                    )
                else:
                    filtered_projects.append(project)

        return filtered_projects, 200


@ns.route("/projects")
class Projects(Resource):

    # Loop through all projects and return the ones
    # that match the user email in the first user item in the user list
    @ns.doc(responses={200: "Success", 401: "Authorization is required"})
    @ns.marshal_with(project_model, as_list=True)
    def get(self):
        owner_email = get_user_email(parser.parse_args())
        data = read_data()
        user_projects = [
            proj
            for proj in data["projects"]
            if any(user["email"] == owner_email for user in proj["user"])
        ]
        return user_projects, 200

    # Add a new project to the list of projects
    # needs certain fields to be present in the JSON payload,
    # the non required will be saved as null if string or emtpy if list
    @ns.marshal_list_with(project_model)
    @ns.doc(
        body=project_model,
        responses={
            201: "Created project",
            401: "Authorization is required",
            406: "Missing JSON data",
            409: "Project with the same name and owner already exists",
        },
    )
    def post(self):
        owner_email = get_user_email(parser.parse_args())

        # Check that required fields are present in the JSON payload
        new_project = ns.payload
        print(new_project)
        if (
            "user" not in new_project
            or "details" not in new_project
            or "email" not in new_project["user"][0]
            or "name" not in new_project["details"][0]
            or "stage" not in new_project
        ):
            abort(406, description="Missing JSON data")

        # Ensure the email is set to owner_email and add 'Editor' role if email matches owner_email
        for user in new_project["user"]:
            if "email" not in user or not user["email"]:
                user["email"] = owner_email
            if user["email"] == owner_email:
                if "roles" not in user:
                    user["roles"] = []
                if "Editor" not in user["roles"]:
                    user["roles"].append("Editor")
        if not any(user["email"] == owner_email for user in new_project["user"]):
            new_project["user"].append(
                {"email": owner_email, "roles": ["Editor"], "grade": ""}
            )

        data = read_data()

        # Check if project with same name exists and has any matching user emails
        new_project_name = new_project["details"][0]["name"]
        new_project_emails = {user["email"] for user in new_project["user"]}

        matching_projects = [
            proj
            for proj in data["projects"]
            if proj["details"][0]["name"] == new_project_name
            and any(user["email"] in new_project_emails for user in proj["user"])
        ]

        if matching_projects:
            proj = matching_projects[0]
            matching_email = next(
                user["email"]
                for user in proj["user"]
                if user["email"] in new_project_emails
            )
            abort(
                409,
                description=f"Project with the same name '{new_project_name}', and owner '{matching_email}' already exists",
            )
        data["projects"].append(new_project)
        write_data(data)

        # Loop through the architecture and add any new items to the array data in S3
        categories = [
            "languages",
            "frameworks",
            "cicd",
            "infrastructure",
            "database",
            "hosting",
        ]
        array_data = read_array_data()

        for category in categories:
            if category in new_project["architecture"]:
                items = []
                if "main" in new_project["architecture"][category]:
                    items.extend(new_project["architecture"][category]["main"])
                if "others" in new_project["architecture"][category]:
                    items.extend(new_project["architecture"][category]["others"])
                if category not in array_data:
                    array_data[category] = []
                array_data[category] = [item.lower() for item in array_data[category]]
                for item in items:
                    item = item.lower()
                    if item not in array_data[category]:
                        array_data[category].append(item)

        write_array_data(array_data)

        return new_project, 201


@ns.doc(
    responses={
        200: "Success",
        401: "Authorization is required",
        404: "Project not found.",
    }
)
@ns.route("/projects/<string:project_name>")
class ProjectDetail(Resource):
    # Loop through all projects and return the one that matches
    # the name and the user email in the first user item in the user list
    @ns.marshal_list_with(project_model)
    def get(self, project_name):
        owner_email = get_user_email(parser.parse_args())

        # Sanitize project_name by replacing '%20' with spaces
        project_name = project_name.replace("%20", " ")

        data = read_data()
        project = next(
            (
                proj
                for proj in data["projects"]
                if proj["details"][0]["name"] == project_name
                and any(user["email"] == owner_email for user in proj["user"])
            ),
            None,
        )
        if not project:
            abort(404, description="Project not found")
        return project, 200

    # Edit a project by taking the whole schema and replacing
    # the existing project with the same name and owner
    @ns.marshal_list_with(project_model)
    @ns.doc(
        body=project_model,
        responses={
            200: "Updated project",
            401: "Authorization is required",
            404: "Project not found",
            406: "Missing JSON data",
        },
    )
    def put(self, project_name):
        owner_email = get_user_email(parser.parse_args())
        updated_project = ns.payload

        if (
            "user" not in updated_project
            or "details" not in updated_project
            or "email" not in updated_project["user"][0]
            or "name" not in updated_project["details"]
        ):
            abort(406, description="Missing JSON data")

        # Ensure the email is set to owner_email
        updated_project["user"][0]["email"] = owner_email

        data = read_data()
        project = next(
            (
                proj
                for proj in data["projects"]
                if proj["details"]["name"] == project_name
                and any(user["email"] == owner_email for user in proj["user"])
            ),
            None,
        )

        if not project:
            abort(404, description="Project not found")

        # Update the project details
        project.update(updated_project)
        write_data(data)

        return project, 200


# Read the client keys from S3 bucket for Cognito
cognito_settings = cognito_data
COGNITO_CLIENT_ID = cognito_settings["COGNITO_CLIENT_ID"]
COGNITO_CLIENT_SECRET = cognito_settings["COGNITO_CLIENT_SECRET"]
REDIRECT_URI = cognito_settings["REDIRECT_URI"]

verifyParser = reqparse.RequestParser()
verifyParser.add_argument(
    "code", location="args", required=True, help="Authorization code is required"
)


@ns.route("/verify")
@ns.doc(
    params={"code": "Authorization code from Cognito callback"},
    responses={200: "Success", 400: "Bad Request"},
)
class VerifyToken(Resource):
    # Route for handling the callback from Cognito
    def get(self):
        # Get the code from the query params
        code = verifyParser.parse_args()["code"]
        if not code:
            logger.error("Authorization code not found")
            return {"error": "Authorization code not found"}, 400

        # Exchange the code for tokens
        token_response = exchange_code_for_tokens(code)

        if "id_token" not in token_response:
            logger.error("Failed to retrieve ID Token")
            return {"error": "Failed to retrieve ID Token"}, 400

        return {
            "id_token": token_response["id_token"],
            "refresh_token": token_response["refresh_token"],
        }, 200


# First version of refreshing a token
refreshParser = reqparse.RequestParser()
refreshParser.add_argument(
    "refresh_token", location="json", required=True, help="Refresh token is required"
)


@ns.route("/refresh")
@ns.doc(
    body=refresh_model,
    responses={200: "Success", 400: "Bad Request", 401: "Unauthorized"},
)
class RefreshToken(Resource):
    # Sending a refresh token to Cognito to get a new ID token.
    # Refresh can be used multiple times to get a new id_token.
    # It kills the old id_token but not the refresh_token.
    def post(self):
        refresh_token = refreshParser.parse_args()["refresh_token"]
        if not refresh_token:
            logger.error("Refresh token not found")
            return {"error": "Refresh token not found"}, 400

        try:
            token_response = exchange_refresh_token_for_id_token(refresh_token)
            return {"id_token": token_response["id_token"]}, 200
        except Exception as e:
            logger.error("Failed to refresh token: %s", str(e))
            return {"error": "Failed to refresh token"}, 401


# Env variable as env may change.
token_url = os.getenv("AWS_COGNITO_TOKEN_URL")


def exchange_refresh_token_for_id_token(refresh_token):
    """Exchange a refresh token for a new ID token from AWS Cognito.

    Args:
        refresh_token (str): The refresh token to exchange

    Returns:
        dict: Response from Cognito containing the new ID token

    Raises:
        Exception: If the token exchange fails, with error details from Cognito
    """
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": COGNITO_CLIENT_ID,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    auth = (COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)

    response = requests.post(
        token_url,
        data=payload,
        headers=headers,
        auth=auth,
        timeout=10,
    )

    if response.status_code != HTTPStatus.OK:
        logger.error("Error: %s, %s", response.status_code, response.text)
        raise Exception(f"Error: {response.status_code}, {response.json()}")

    return response.json()


def exchange_code_for_tokens(code):
    """Exchange an authorization code for access and refresh tokens from AWS Cognito.

    Args:
        code (str): The authorization code received from the OAuth2 authorization flow.

    Returns:
        dict: Response from Cognito containing access and refresh tokens.

    Raises:
        Exception: If the token exchange fails, with error details from Cognito.
    """
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{REDIRECT_URI}/api/v1/verify",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    auth = (COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)
    response = requests.post(
        token_url,
        data=payload,
        headers=headers,
        auth=auth,
        timeout=10,
    )

    if response.status_code != HTTPStatus.OK:
        if response.json()["error"] == "invalid_grant":
            logger.error("Invalid authorization code")
            return {"error": "Invalid authorization code"}, 404
        logger.error("Error: %s, %s", response.status_code, response.text)
        raise Exception(f"Error: {response.status_code}, {response.json()}")

    # Return the parsed JSON response
    return response.json()
