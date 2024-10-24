from flask_restx import Resource, Namespace, reqparse, abort
from .api_models import get_project_model
from .utils import read_data, write_data, read_array_data, write_array_data, verify_cognito_token, read_client_keys
import boto3
from botocore.exceptions import ClientError
import logging
import os
import requests


ns = Namespace('/api/', path="/api/", description="")


parser = reqparse.RequestParser()
parser.add_argument('Authorization', location='headers', required=True, help='Authorization header is required')

required_param = {'Authorization': 'ID Token required'}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_user_email(args):
    token = args['Authorization']    
    try:
        user_attributes = verify_cognito_token(token)
        owner_email = user_attributes['email']        
        if not owner_email:
            logger.error("No email found in user attributes")
            abort(401, description="Not authorized")
        
        return owner_email
    except Exception as e:
        logger.exception("Error verifying token")
        abort(401, description="Not authorized")


@ns.route("/user")
class User(Resource):
    @ns.doc(responses={200: 'Success', 401: 'Authorization is required'})
    def get(self):
        owner_email = get_user_email(parser.parse_args())
        return {'email': owner_email}, 200

filterParser = reqparse.RequestParser()
filterParser.add_argument('email', location="args", action="split", required=False, help='User email to filter by')
filterParser.add_argument('roles', location="args", action="split", required=False, help='Roles to filter by')
filterParser.add_argument('name', location="args", action="split", required=False, help='Project name to filter by')
filterParser.add_argument('developed', location="args", action="split", required=False, help='Developed partners to filter by')
filterParser.add_argument('languages', location="args", action="split", required=False, help='Languages to filter by')
filterParser.add_argument('source_control', location="args", action="split", required=False, help='Source control to filter by')
filterParser.add_argument('hosting', location="args", action="split", required=False, help='Hosting type to filter by')
filterParser.add_argument('database', location="args", action="split", required=False, help='Database to filter by')
filterParser.add_argument('frameworks', location="args", action="split", required=False, help='Frameworks to filter by')
filterParser.add_argument('CICD', location="args", action="split", required=False, help='CI/CD tools to filter by')
filterParser.add_argument('infrastructure', location="args", action="split", required=False, help='Infrastructure to filter by')
filterParser.add_argument('return', location="args", action="split", required=False, help='Sections to return: user, details, developed, source_control, architecture, or whole project')

@ns.route("/projects/filter")
class Filter(Resource):
    @ns.doc(params={'email':'User email to filter by', 'roles':'Roles to filter by', 'name':'Project name to filter by', 'developed':'Developed partners or "In house, partnership or outsourced" to filter by', 'languages':'Languages to filter by', 'source_control':'Source control to filter by', 'hosting':'Hosting type to filter by', 'database':'Database to filter by', 'frameworks':'Frameworks to filter by', 'CICD':'CI/CD tools to filter by', 'infrastructure':'Infrastructure to filter by', 'return':'Sections to return: user, details, developed, source_control, architecture, or whole project'},
        responses={200: 'Success', 401: 'Authorization is required'})
    def get(self):
        owner_email = get_user_email(parser.parse_args())
        args = filterParser.parse_args()

        # Extract filter parameters from the request, ignoring missing/empty ones
        filter_params = {key: value for key, value in args.items() if key not in required_param and value}
        print(filter_params)

        # Read all projects
        data = read_data()
        projects = data['projects']
        
        # Filter projects based on query params
        filtered_projects = []
        
        for project in projects:
            match = True

            # Filter by email
            if 'email' in filter_params:
                project_emails = [user['email'].lower() for user in project['user']]
                if not any(email.lower() in project_emails for email in filter_params['email']):
                    match = False
            
            # Filter by roles
            if 'roles' in filter_params:
                project_roles = [role.lower() for user in project['user'] for role in user['roles']]
                if not any(role.lower() in project_roles for role in filter_params['roles']):
                    match = False

            # Filter by project name (partial match)
            if 'name' in filter_params:
                if not any(name.lower() in project['details']['name'].lower() for name in filter_params['name']):
                    match = False

            # Filter by developed partners
            if 'developed' in filter_params:
                for dev_value in filter_params['developed']:
                    dev_value_lower = dev_value.lower()
                    
                    # Check first part (In House, Partnership, Outsourced)
                    developed_type = project['developed'][0].lower()
                    if dev_value_lower == developed_type:
                        continue
                    
                    # Check second part (list of company/partner names)
                    developed_partners = project['developed'][1]
                    if developed_partners:
                        developed_partners_lower = [d.lower() for d in developed_partners if d]
                        if any(dev_value_lower in partner for partner in developed_partners_lower):
                            continue
                    
                    # If neither part matches, break out of loop
                    match = False
                    break

            # Filter by source control
            if 'source_control' in filter_params:
                project_source_control = project['source_control']
                for sc_filter in filter_params['source_control']:
                    sc_filter_lower = sc_filter.lower()
                    match_found = False
                    for sc in project_source_control:
                        if sc_filter_lower in sc['type'].lower():
                            match_found = True
                            break
                        for link in sc['links']:
                            if sc_filter_lower in link['description'].lower() or sc_filter_lower in link['url'].lower():
                                match_found = True
                                break
                        if match_found:
                            break
                    if not match_found:
                        match = False
                        break

            # Filter by hosting type
            if 'hosting' in filter_params:
                hosting_types = [project['architecture']['hosting']['type'].lower()] + [h.lower() for h in project['architecture']['hosting']['detail']]
                if not any(ht.lower() in hosting_types for ht in filter_params['hosting']):
                    match = False

            # Filter by database
            if 'database' in filter_params:
                databases = [db.lower() for db in project['architecture']['database']['main']] + [db.lower() for db in project['architecture']['database']['others']]
                if not any(db.lower() in databases for db in filter_params['database']):
                    match = False

            # Filter by frameworks
            if 'frameworks' in filter_params:
                frameworks = [fw.lower() for fw in project['architecture']['frameworks']['main']] + [fw.lower() for fw in project['architecture']['frameworks']['others']]
                if not any(fw.lower() in frameworks for fw in filter_params['frameworks']):
                    match = False

            # Filter by CICD tools
            if 'CICD' in filter_params:
                cicd_tools = [c.lower() for c in project['architecture']['CICD']['main']] + [c.lower() for c in project['architecture']['CICD']['others']]
                if not any(c.lower() in cicd_tools for c in filter_params['CICD']):
                    match = False

            # Filter by infrastructure
            if 'infrastructure' in filter_params:
                infrastructure = [inf.lower() for inf in project['architecture']['infrastructure']['main']] + [inf.lower() for inf in project['architecture']['infrastructure']['others']]
                if not any(inf.lower() in infrastructure for inf in filter_params['infrastructure']):
                    match = False

            if match:
                if 'return' in filter_params:
                    sections_to_return = filter_params['return']
                    partial_project = {}
                    
                    for section in sections_to_return:
                        section = section.lower()
                        if section == 'user':
                            partial_project['user'] = project['user']
                        elif section == 'details':
                            partial_project['details'] = project['details']
                        elif section == 'developed':
                            partial_project['developed'] = project['developed']
                        elif section == 'source_control':
                            partial_project['source_control'] = project['source_control']
                        elif section == 'architecture':
                            partial_project['architecture'] = project['architecture']
                    
                    filtered_projects.append(partial_project)
                else:
                    filtered_projects.append(project) 

        return filtered_projects, 200


@ns.route("/projects")
class Projects(Resource):
    @ns.doc(responses={200: 'Success', 401: 'Authorization is required'})
    @ns.marshal_with(get_project_model(), as_list=True)
    def get(self):
        owner_email = get_user_email(parser.parse_args())
        data = read_data()
        user_projects = [proj for proj in data['projects'] if proj["user"][0]['email'] == owner_email]
        return user_projects, 200
    
    @ns.marshal_list_with(get_project_model())
    @ns.doc(responses={201: 'Created project', 401: 'Authorization is required', 406: 'Missing JSON data', 409: 'Project with the same name and owner already exists'})
    def post(self):
        owner_email = get_user_email(parser.parse_args())

        new_project = ns.payload
        print(new_project)
        if 'user' not in new_project or 'details' not in new_project or 'email' not in new_project['user'][0] or 'name' not in new_project['details'][0] or 'archived' not in new_project:
            abort(406, description="Missing JSON data")
        
        # Ensure the email is set to owner_email
        for user in new_project['user']:
            if 'email' not in user or not user['email']:
                user['email'] = owner_email
        
        data = read_data()

        for proj in data['projects']:
            for new_proj_user in new_project['user']:
                for proj_user in proj['user']:
                    print(proj['details'])
                    if proj['details'][0]['name'] == new_project['details'][0]['name'] and proj_user['email'] == new_proj_user['email']:
                        abort(409, description=f"Project with the same name '{proj['details'][0]['name']}' and owner '{proj_user['email']}' already exists")
        data['projects'].append(new_project)
        write_data(data)
        
        categories = ['languages', 'frameworks', 'cicd', 'infrastructure']
        array_data = read_array_data()

        for category in categories:
            if category in new_project["architecture"]:
                items = []
                if 'main' in new_project["architecture"][category]:
                    items.extend(new_project["architecture"][category]['main'])
                if 'others' in new_project["architecture"][category]:
                    items.extend(new_project["architecture"][category]['others'])
                if category not in array_data:
                    array_data[category] = []
                array_data[category] = [item.lower() for item in array_data[category]]
                for item in items:
                    item = item.lower()
                    if item not in array_data[category]:
                        array_data[category].append(item)
        
        write_array_data(array_data)
        
        return new_project, 201


@ns.doc(responses={200: 'Success', 401: 'Authorization is required', 404: 'Project not found.'})
@ns.route("/projects/<string:project_name>")
class ProjectDetail(Resource):
    @ns.marshal_list_with(get_project_model())
    def get(self, project_name):
        owner_email = get_user_email(parser.parse_args())

        # Sanitize project_name by replacing '%20' with spaces
        project_name = project_name.replace('%20', ' ')

        data = read_data()
        project = next((proj for proj in data['projects'] if proj["details"][0]['name'] == project_name and any(user['email'] == owner_email for user in proj["user"])), None)
        if not project:
            abort(404, description="Project not found")
        return project, 200

    @ns.marshal_list_with(get_project_model())
    @ns.doc(responses={200: 'Updated project', 401: 'Authorization is required', 404: 'Project not found', 406: 'Missing JSON data'})
    def put(self, project_name):
        owner_email = get_user_email(parser.parse_args())
        updated_project = ns.payload

        if 'user' not in updated_project or 'details' not in updated_project or 'email' not in updated_project['user'][0] or 'name' not in updated_project['details']:
            abort(406, description="Missing JSON data")

        # Ensure the email is set to owner_email
        updated_project['user'][0]['email'] = owner_email

        data = read_data()
        project = next((proj for proj in data['projects'] if proj["details"]['name'] == project_name and any(user['email'] == owner_email for user in proj["user"])), None)

        if not project:
            abort(404, description="Project not found")

        # Update the project details
        project.update(updated_project)
        write_data(data)

        return project, 200

autoCompleteParser = reqparse.RequestParser()
autoCompleteParser.add_argument('type', type=str, required=True, help='type is required')
autoCompleteParser.add_argument('search', type=str, required=True, help='search is required')

@ns.doc(params={'type':'Type of array', 'search':'Search query'}, 
responses={200: 'Success', 400: 'type and search are required', 404: 'No matches found.', 406: 'Invalid type', 411: 'Search query is too long'})
@ns.route("/autocomplete")
class Autocomplete(Resource):
    def get(self):
        owner_email = get_user_email(parser.parse_args())

        args = autoCompleteParser.parse_args()
        search_type = args['type']
        search_query = args['search']

        if not search_type or not search_query:
            abort(400, description="type and search are required")
        
        if search_type not in ['languages', 'frameworks', 'source control', 'cicd', 'infrastructure', "architecture", "database"]:
            abort(406, description="Invalid type")
        
        if len(search_query) > 16:
            abort(411, description="Search query is too long")
        
        array_data = read_array_data()
        
        if search_type not in array_data:
            abort(406, description=f"Invalid type: {search_type}")
        
        results = [item for item in array_data[search_type] if search_query.lower() in item.lower()]

        if not results:
            abort(404, description="No matches found")
        
        return results, 200

cognito_settings = read_client_keys()
COGNITO_CLIENT_ID = cognito_settings["AWS_COGNITO_CLIENT_ID"]
COGNITO_CLIENT_SECRET = cognito_settings["AWS_COGNITO_CLIENT_SECRET"]
REDIRECT_URI = cognito_settings["REDIRECT_URI"]
# REDIRECT_URI = 'http://localhost:8000/api/verify'

verifyParser = reqparse.RequestParser()
verifyParser.add_argument('code', location='args', required=True, help='Authorization code is required')
@ns.route("/verify")
class VerifyToken(Resource):
    # Route for handling the callback from Cognito
    def get(self):
        # Get the code from the query params
        code = verifyParser.parse_args()['code']
        if not code:
            logger.error("Authorization code not found")
            return {"error": "Authorization code not found"}, 400

        # Exchange the code for tokens
        token_response = exchange_code_for_tokens(code)

        if 'id_token' not in token_response:
            logger.error("Failed to retrieve ID Token")
            return {"error": "Failed to retrieve ID Token"}, 400

        return {"id_token": token_response['id_token'], "refresh_token": token_response["refresh_token"]}, 200

refreshParser = reqparse.RequestParser()
refreshParser.add_argument('refresh_token', location='json', required=True, help='Refresh token is required')

@ns.route("/refresh")
class RefreshToken(Resource):
    def get(self):
        refresh_token = refreshParser.parse_args()['refresh_token']
        if not refresh_token:
            logger.error("Refresh token not found")
            return {"error": "Refresh token not found"}, 400

        token_response = exchange_refresh_token_for_id_token(refresh_token)

        if 'id_token' not in token_response:
            logger.error("Failed to retrieve ID Token")
            return {"error": "Failed to retrieve ID Token"}, 400

        return {"id_token": token_response['id_token']}, 200
    

def exchange_refresh_token_for_id_token(refresh_token):
    token_url = f"https://keh-tech-audit-tool.auth.eu-west-2.amazoncognito.com/oauth2/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
        }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_url, data=payload, headers=headers, auth = (COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET))

    if response.status_code != 200:
        logger.error(f"Error: {response.status_code}, {response.text}")
        raise Exception(f"Error: {response.status_code}, {response.json()}")

    return response.json()

def exchange_code_for_tokens(code):
    token_url = f"https://keh-tech-audit-tool.auth.eu-west-2.amazoncognito.com/oauth2/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': f'{REDIRECT_URI}/api/verify'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    auth = (COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)

    response = requests.post(token_url, data=payload, headers=headers, auth=auth)

    if response.status_code != 200:
        if response.json()['error'] == 'invalid_grant':
            logger.error("Invalid authorization code")
            return {"error": "Invalid authorization code"}, 404
        logger.error(f"Error: {response.status_code}, {response.text}")
        raise Exception(f"Error: {response.status_code}, {response.json()}")

    # Return the parsed JSON response
    return response.json()