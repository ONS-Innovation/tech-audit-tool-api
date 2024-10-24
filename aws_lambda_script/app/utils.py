
from flask_restx import abort
from botocore.exceptions import ClientError
from jwt.algorithms import RSAAlgorithm
import json
import os
import boto3
import jwt
import requests
import json

bucket_name = "keh-tech-audit-tool"
object_name = "new_project_data.json"
autocomplete_object_name = "array_data.json"
region_name = os.getenv("AWS_DEFAULT_REGION")

s3 = boto3.client('s3', region_name=region_name)

def read_client_keys():
    client_keys_object_name = "client_keys.json"
    try:
        response = s3.get_object(Bucket=bucket_name, Key=client_keys_object_name)
        client_keys = json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            client_keys = {}
        else:
            abort(500, description=f"Error reading client keys: {e}")
    return client_keys


def read_data():
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_name)
        data = json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            data = {'projects': []}
        else:
            abort(500, description=f"Error reading data: {e}")
    return data

def write_data(new_data):
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=json.dumps(new_data, indent=4).encode('utf-8')
        )
    except ClientError as e:
        abort(500, description=f"Error writing data: {e}")



def read_array_data():
    try:
        response = s3.get_object(Bucket=bucket_name, Key=autocomplete_object_name)
        array_data = json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            array_data = {}
        else:
            abort(500, description=f"Error reading array data: {e}")
    return array_data

def write_array_data(new_array_data):
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=autocomplete_object_name,
            Body=json.dumps(new_array_data, indent=4).encode('utf-8')
        )
    except ClientError as e:
        abort(500, description=f"Error writing array data: {e}")



COGNITO_REGION = 'eu-west-2'  # e.g. us-east-1
USER_POOL_ID = 'eu-west-2_cv6SLP60y'

def get_cognito_jwks():
    # Get the JWKS from the cognito user pool
    jwks_url = f'https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json'
    response = requests.get(jwks_url)
    if response.status_code == 200:
        return response.json()
    else:
        abort(401, description="Unable to fetch JWKS")

def verify_cognito_token(id_token):
    jwks = get_cognito_jwks()

    try:
        # Decode the ID token without verification to get the header and find the key ID
        unverified_header = jwt.get_unverified_header(id_token)
        key_id = unverified_header['kid']

        # Find the correct public key in the JWKS
        public_key = None
        for key in jwks['keys']:
            if key['kid'] == key_id:
                public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                break

        if public_key is None:
            abort(401, description="Public key not found in JWKS")

        # Now verify the token
        decoded_token = jwt.decode(
            id_token,
            public_key,
            algorithms=['RS256'],
            audience='dm3289s0tqtsr5qn2qm5i9fql',  # Set this to your app client ID
            issuer=f'https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}'
        )
        return decoded_token  # Return the decoded token (contains claims like user attributes)
    
    except jwt.ExpiredSignatureError:
        abort(401, description="Token is expired")
    except jwt.InvalidTokenError as e:
        abort(401, description=f"Invalid token: {str(e)}")