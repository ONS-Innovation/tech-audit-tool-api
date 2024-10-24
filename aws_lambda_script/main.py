import awsgi
from app import create_app

app = create_app()

def lambda_handler(event, context):
    # Call the awsgi response which handles the Flask app request
    response = awsgi.response(app, event, context)
    
    # Add the necessary CORS headers to the response
    response['headers']['Access-Control-Allow-Origin'] = '*'
    response['headers']['Access-Control-Allow-Methods'] = 'OPTIONS,POST,GET'
    response['headers']['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    return response