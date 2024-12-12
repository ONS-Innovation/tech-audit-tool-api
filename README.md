
# Tech Audit Tool - API

A Flask and flask-restx API for the tech audit tool.

## Setting up & Running Locally

Clone the project

```bash
git clone https://github.com/ONS-Innovation/keh-tech-audit-tool-api.git
```

Install dependencies

```bash
make install
```

Install dev dependencies to run linting tools

```bash
make install-dev
```

Set environment variables:

```bash
export TECH_AUDIT_DATA_BUCKET='sdp-dev-tech-audit-tool-api'
export TECH_AUDIT_SECRET_MANAGER='sdp-dev-tech-audit-tool-api/secrets'
export AWS_COGNITO_TOKEN_URL='https://tech-audit-tool-api-sdp-dev.auth.eu-west-2.amazoncognito.com/oauth2/token'
```

Go to the aws_lambda_script directory

```bash
cd aws_lambda_script
```

Run the project locally

```bash
poetry run python3 -m app
```


## Testing

This repo utilises PyTest for the testing. Please make sure you have installed dev dependencies before running tests.

To test you need a mock token. Visit this [link](https://tech-audit-tool-api-sdp-dev.auth.eu-west-2.amazoncognito.com/login?client_id=7hdpes1atnuepl1ffvf21a28r3&response_type=code&scope=email+openid&redirect_uri=https://tech-audit-tool-api.sdp-dev.aws.onsdigital.uk/api/v1/verify) and copy the `id_token`.

Then import the token into your environment:

```bash
export MOCK_TOKEN=<id_token>
```

Make sure dev dependencies are installed:
```bash
make install-dev
```

When in root directory, run the testing command. If you are in `aws_lambda_script` it will fail.
```bash
make pytest
```

If all tests fail, please relogin [here](https://tech-audit-tool-api-sdp-dev.auth.eu-west-2.amazoncognito.com/login?client_id=7hdpes1atnuepl1ffvf21a28r3&response_type=code&scope=email+openid&redirect_uri=https://tech-audit-tool-api.sdp-dev.aws.onsdigital.uk/api/v1/verify) to the Cognito and use a new token.

Once you have finished testing, clean the temp files with:
```bash
make clean
```

## Testing with Postman

View the Postman workspace for this project [here](https://www.postman.com/science-pilot-55892832/workspace/keh-tech-audit-tool-api/collection/38871441-e42f661e-6430-4f46-8182-083e9e0fd4ad?action=share&creator=38871441&active-environment=38871441-7c5e3795-74f5-46b3-9034-637561aba746).

Please read the description or README to understand how to use this workspace. You need to get a mock_token to authenticate yourself in each request.

## Testing with Swagger UI

View the Swagger UI [here](https://tech-audit-tool-api.sdp-sandbox.aws.onsdigital.uk/).

Retrieve your `id_token`, go to the URL above, click the green outlined button with the text `Authorize` and enter your `id_token` in the `Value` box. Click the green outlined `Authorize` button. 

Now you can go through the /api/v1/ routes and test the endpoints.

## MkDocs Documentation

To install the dependencies for the MkDocs, run the following command:

```bash
make install-docs
```

Then run the following command to run the MkDocs:

```bash
make mkdocs
```

Deploying the MkDocs is done by running the following command:

```bash
make mkdocs-build
```

Then changing the name of the `site` directory to `mkdocs_deployment`.

## API Reference

Before testing the API, you need to use the above instructions at **Testing** to get a mock token, as all requests need to be authenticated.

| Header | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | **Required**. ID Token (Not access) |
 
### Get user email

```http
GET /api/v1/user
```

Get's the users email.

### Get new ID token from refresh token

```http
POST /api/v1/refresh
```

| Body | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `refresh_token`      | `string` | **Required**. The refresh token |

Get's a new id_token from a refresh token. Old id_token is killed, refresh_token
can be used multiple times to get a new id_token.

### Get all user projects

```http
GET /api/v1/projects
```

Get's the projects associated with the users email.

### Get a specific user project

```http
GET /api/v1/projects/<project_name>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `<project_name>`      | `string` | **Required**. The project you want to get |


Get's a specific project from the user.

### Create a new project

```http
POST /api/v1/projects/
```

Send JSON in this format:
```JSON
{
    "user": [
      {
        "email": "Email",
        "roles": ["Technical Contact"],
        "grade": "Grade"
      },
      {
        "email": "Email",
        "roles": ["Delivery Manager Contact"],
        "grade": "Grade"
      }
    ],
    "details":[ 
      {
        "name": "Name",
        "short_name": "Short Name",
        "documentation_link": ["List of strings"],
        "project_description": "Description"
      }]
    ,
    "developed": ["In-house", []],
    "source_control": [
      {
        "type": "GitHub",
        "links": [
          {
            "description": "Description",
            "url": "URL"
          }
        ]
      }
    ],
    "architecture": {
      "hosting": {
        "type": ["Hybrid"],
        "details": ["List of strings"]
      },
      "database": {
        "main": [],
        "others": ["List of strings"]
      },
      "languages": {
        "main": ["List of strings"],
        "others": ["List of strings"]
      },
      "frameworks": {
        "main": [],
        "others": ["List of strings"]
      },
      "cicd": {
        "main": [],
        "others": ["List of strings"]
      },
      "infrastructure": {
        "main": [],
        "others": ["List of strings"]
      }
    },
    "stage":"Development"
  }
```
Creates a project. If the languages, database, frameworks, cicd, infrastructure or source control is not in the `array_data.json` bucket, then it is added.


### Get autocomplete from string [REMOVED]

```http
GET /api/v1/autocomplete
```
Removed as autocomplete is processed on front-end.


### Get filtered projects 

```http
GET /api/v1/projects/filter
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `<filter>`      | `string` | **Required**. The specific filter. Multiple filter seperated by a comma (,) |
| `<return>`      | `string` | What you want returned from the project. Multiple return filter seperated by a comma (,) |


Get's projects using a filter.

Filter can be one or more of: email, roles, name, developed, source_control, hosting, database, languages, frameworks, cicd, infrastructure.

Return can be one or more of: user, details, developed, source_control, architecture.


### Edit a project

```http
PUT /api/v1/projects/{project_name}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `<project_name>`      | `string` | **Required**. The project you want to get |


Send JSON in this format:
```JSON
{
    "user": [
      {
        "email": "Email",
        "roles": ["Technical Contact"],
        "grade": "Grade"
      },
      {
        "email": "Email",
        "roles": ["Delivery Manager Contact"],
        "grade": "Grade"
      }
    ],
    "details":[ 
      {
        "name": "Name",
        "short_name": "Short Name",
        "documentation_link": ["List of strings"],
        "project_description": "Description"
      }]
    ,
    "developed": ["In-house", []],
    "source_control": [
      {
        "type": "GitHub",
        "links": [
          {
            "description": "Description",
            "url": "URL"
          }
        ]
      }
    ],
    "architecture": {
      "hosting": {
        "type": ["Hybrid"],
        "details": ["List of strings"]
      },
      "database": {
        "main": [],
        "others": ["List of strings"]
      },
      "languages": {
        "main": ["List of strings"],
        "others": ["List of strings"]
      },
      "frameworks": {
        "main": [],
        "others": ["List of strings"]
      },
      "cicd": {
        "main": [],
        "others": ["List of strings"]
      },
      "infrastructure": {
        "main": [],
        "others": ["List of strings"]
      }
    },
    "stage":"Development"
  }
```
Edits a project by checking if the languages, database, frameworks, cicd, infrastructure, or source control are missing from the `array_data.json` bucket. If any are missing, they are added.


## Authorization with Cognito and API Gateway

Visiting the [Cognito UI](https://keh-tech-audit-tool.auth.eu-west-2.amazoncognito.com/oauth2/authorize?client_id=dm3289s0tqtsr5qn2qm5i9fql&response_type=code&scope=email+openid+phone&redirect_uri=https%3A%2F%2Fdutwj6q915.execute-api.eu-west-2.amazonaws.com%2Fdev%2Fapi%2Fverify), and successfully logging in, will redirect you to:

```bash
/api/v1/verify?code=<code>
```

This returns your token, which you can use in testing the authentication on the API. Use this token in the Authorization header to authenticate your requests.

The /api/v1/verify route get's the client keys and redirect uri from the bucket.

