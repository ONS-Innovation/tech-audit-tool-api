import pytest
import json
import os
import datetime
from unittest.mock import patch
from app.utils import write_data, write_array_data

# Mock verify_cognito_token for authentication
mocked_user_email = "test@ons.gov.uk"

def mock_verify_cognito_token(token):
    return {'email': mocked_user_email}

# Mock reading data function
def mock_read_data():
    return {
        'projects': [
            {
                'details': {'name': 'Test Project'},
                'user': [{'email': mocked_user_email}],
                'architecture': {'languages': {'main': 'python', 'others': ['javascript']}}
            }
        ]
    }

# Mock reading array data
def mock_read_array_data():
    return {'languages': ['python', 'javascript', 'java'], 'IDEs': ['vscode', 'pycharm'], 'misc': ['git']}

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Helper to get mock token from environment
def get_mock_token():
    mock_token = os.getenv('MOCK_TOKEN')
    print(mock_token)
    if not mock_token:
        raise EnvironmentError("MOCK_TOKEN environment variable is not set. Please set it to run the tests.")
    return mock_token

# Test for "/user" route
@patch('app.utils.verify_cognito_token', side_effect=mock_verify_cognito_token)
def test_get_user(mock_verify_token, client):
    mock_token = get_mock_token()
    response = client.get('/api/user', headers={'Authorization': f'{mock_token}'})
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, {response.data}"
    data = json.loads(response.data)
    assert data['email'] == mocked_user_email

# Test for "/projects" route - GET
@patch('app.utils.read_data', side_effect=mock_read_data)
@patch('app.utils.verify_cognito_token', side_effect=mock_verify_cognito_token)
def test_get_projects(mock_verify_token, mock_read, client):
    mock_token = get_mock_token()
    response = client.get('/api/projects', headers={'Authorization': f'{mock_token}'})
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, {response.data}"
    data = json.loads(response.data)
    assert 'Test Project' in data[-1]['details'][0]['name']

# Test for POSTing a new project with a timestamp in the name
@patch('app.utils.read_data', side_effect=mock_read_data)
@patch('app.utils.verify_cognito_token', side_effect=mock_verify_cognito_token)
@patch('app.utils.write_data')
def test_post_and_get_project_with_timestamp(mock_write_data, mock_verify_token, mock_read, client):
    mock_token = get_mock_token()
    
    # Create a unique project name using time.time()
    project_name = f"Test Project {datetime.datetime.now(datetime.UTC)}"
    
    new_project = {
        'user': [{'email': ''}],  # email will be replaced by the user's email
        'details': {'name': project_name},
        'architecture': {'languages': {'main': 'ruby', 'others': ['php']}}
    }
    
    # POST the new project
    post_response = client.post(
        '/api/projects',
        data=json.dumps(new_project),
        headers={'Authorization': f'{mock_token}', 'Content-Type': 'application/json'}
    )
    
    assert post_response.status_code == 201, f"Unexpected status code: {post_response.status_code}, {post_response.data}"
    
    # GET the project by name
    get_response = client.get(f'/api/projects/{project_name}', headers={'Authorization': f'{mock_token}'})
    assert get_response.status_code == 200, f"Unexpected status code: {get_response.status_code}, {get_response.data}"
    data = json.loads(get_response.data)
    assert data['details'][0]['name'] == project_name
    assert data['user'][0]['email'] == mocked_user_email

# Tests for "/autocomplete" route
@patch('app.utils.read_array_data', side_effect=mock_read_array_data)
@patch('app.utils.verify_cognito_token', side_effect=mock_verify_cognito_token)
def test_autocomplete_languages(mock_verify_token, mock_read_array, client):
    mock_token = get_mock_token()
    response = client.get('/api/autocomplete', query_string={'type': 'languages', 'search': 'py'}, headers={'Authorization': f'{mock_token}'})
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, {response.data}"
    data = json.loads(response.data)
    assert 'python' in data

@patch('app.utils.verify_cognito_token', side_effect=mock_verify_cognito_token)
def test_autocomplete_invalid_type(mock_verify_token, client):
    mock_token = get_mock_token()
    response = client.get('/api/autocomplete', query_string={'type': 'unknown', 'search': 'py'}, headers={'Authorization': f'{mock_token}'})
    assert response.status_code == 406, f"Unexpected status code: {response.status_code}, {response.data}"

@patch('app.utils.verify_cognito_token', side_effect=mock_verify_cognito_token)
def test_autocomplete_query_too_long(mock_verify_token, client):
    mock_token = get_mock_token()
    response = client.get('/api/autocomplete', query_string={'type': 'languages', 'search': 'p' * 17}, headers={'Authorization': f'{mock_token}'})
    assert response.status_code == 411, f"Unexpected status code: {response.status_code}, {response.data}"

# Test for "/verify" route
@patch('app.resources.exchange_code_for_tokens', return_value={'id_token': 'mockidtoken'})
def test_verify_token(mock_exchange, client):
    mock_token = get_mock_token()
    response = client.get('/api/verify', query_string={'code': 'mockcode'}, headers={'Authorization': f'{mock_token}'})
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, {response.data}"
    data = json.loads(response.data)
    assert data['id_token'] == 'mockidtoken'
