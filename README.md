
# KEH | Tech Audit Tool - API

A Flask and flask-restx API for the tech audit tool.

## Setting up & Running Locally

Clone the project

```bash
git clone https://github.com/ONS-Innovation/keh-tech-audit-tool-api
```

Install dependencies

```bash
make install
```

Install dev dependencies to run linting tools

```bash
make install-dev
```

Import secrets

```bash
export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
export AWS_DEFAULT_REGION=eu-west-2 
export AWS_SECRET_NAME=github-tooling-suite/onsdigital
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

To test you need a mock token. Visit this [link](https://keh-tech-audit-tool.auth.eu-west-2.amazoncognito.com/login?client_id=dm3289s0tqtsr5qn2qm5i9fql&response_type=code&scope=email+openid+phone&redirect_uri=https://dutwj6q915.execute-api.eu-west-2.amazonaws.com/dev/api/verify) and copy the `id_token`.

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

If all tests fail, please relogin [here](https://keh-tech-audit-tool.auth.eu-west-2.amazoncognito.com/login?client_id=dm3289s0tqtsr5qn2qm5i9fql&response_type=code&scope=email+openid+phone&redirect_uri=https://dutwj6q915.execute-api.eu-west-2.amazonaws.com/dev/api/verify) to the Cognito and use a new token.

Once you have finished testing, clean the temp files with:
```bash
make clean
```

## Testing with Postman

View the Postman workspace for this project [here](https://www.postman.com/science-pilot-55892832/workspace/keh-tech-audit-tool-api/collection/38871441-e42f661e-6430-4f46-8182-083e9e0fd4ad?action=share&creator=38871441&active-environment=38871441-7c5e3795-74f5-46b3-9034-637561aba746).

Please read the description or README to understand how to use this workspace. You need to get a mock_token to authenticate yourself in each request.

## API Reference

Before testing the API, you need to use the above instructions at **Testing** to get a mock token, as all requests need to be authenticated.

| Header | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | **Required**. ID Token (Not access) |

### Get user email

```http
GET /api/user
```

Get's the users email.

### Get all user projects

```http
GET /api/projects
```

Get's the projects associated with the users email.

### Get a specific user project

```http
GET /api/projects/<project_name>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `<project_name>`      | `string` | **Required**. The project you want to get |


Get's a specific project from the user.

### Create a new project

```http
POST /api/projects/
```

Send JSON in this format:
```JSON
{
  "user": [
    {
      "email": "String",
      "roles": ["String"],
      "grade": "String"
    },
    {
      "email": "String",
      "roles": ["String"],
      "grade": "String"
    }
  ],
  "details": [
    {
      "name": "String",
      "short_name": "String",
      "documentation_link": ["String"],
      "project_description": "String"
    }
  ],
  "developed": ["String", ["String", "String"]],
  "source_control": [
    {
      "type": "String",
      "links": [
        {
          "description": "String",
          "url": "String"
        },
        {
          "description": "String",
          "url": "String"
        }
      ]
    }
  ],
  "architecture": {
    "hosting": {
      "type": "String",
      "details": ["String", "String"]
    },
    "database": {
      "main": ["String", "String"],
      "others": ["String"]
    },
    "languages": {
      "main": ["String", "String"],
      "others": ["String", "String"]
    },
    "frameworks": {
      "main": ["String", "String"],
      "others": ["String", "String"]
    },
    "CICD": {
      "main": ["String", "String"],
      "others": ["String", "String"]
    },
    "infrastructure": {
      "main": ["String", "String"],
      "others": ["String", "String"]
    }
  },
  "archived": false
}
```
Create's a project. If the languages, database, frameworks, CICD, infrastructure or source control, is not in the array_data.json bucket then it is added.


### Get autocomplete from string

```http
GET /api/autocomplete
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `type` | `string` | **Required**. The type of array ie. languages. |
| `search` | `string` | **Required**. The string needing autocomplete. |

Returns a list of potential autocomplete.

Example REQUEST: 
```bash
GET http://localhost:5000/api/autocomplete?type=languages&search=script
```

Example RESPONSE:
```JSON
[
    "javascript",
    "typescript",
    "actionscript",
    "postscript",
    "jscript"
]
```


### Get filtered projects 

```http
GET /api/projects/filter
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `<filter>`      | `string` | **Required**. The specific filter. Multiple filter seperated by a comma (,) |
| `<return>`      | `string` | What you want returned from the project. Multiple return filter seperated by a comma (,) |


Get's projects using a filter.

Filter can one or more of: email, roles, name, developed, source_control, hosting, database, languages, frameworks, cicd, infrastructure.

Return can be one or more of: user, details, developed, source_control, architecture.


### Edit a project

```http
PUT /api/projects/{project_name}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `<project_name>`      | `string` | **Required**. The project you want to get |


Send JSON in this format:
```JSON
{
    "user": [ 
        {
            "email": "",
            "roles": [
                "owner"
            ]
        }
    ],
    "details": {
        "name": "Project1",
        "short_name": "This is project 1",
        "documentation_link": ""
    },
    "developed":[  
        "Partnership",
        ["ONS", "GDS"]
    ],
    "source_control":[
        "GitHub"
    ],
    "architecture": {
        "hosting": {"type": "Hybrid", "detail": ["AWS", "Local"]},
        "database": {"main": "MongoDB", "others": ["DocumentDB"]},
        "languages": {"main": "Python", "others": ["JavaScript", "Java"]},
        "frameworks": {"main": "React", "others": []},
        "CICD": {"main": "Python", "others": ["JavaScript", "Java"]},
        "infrastructure": {"main": "Python", "others": []}
    }
}
```
Create's a project. If the languages, database, frameworks, CICD, infrastructure or source control, is not in the array_data.json bucket then it is added.


## Authorization with Cognito and API Gateway

Visiting the [Cognito UI](https://keh-tech-audit-tool.auth.eu-west-2.amazoncognito.com/oauth2/authorize?client_id=dm3289s0tqtsr5qn2qm5i9fql&response_type=code&scope=email+openid+phone&redirect_uri=https%3A%2F%2Fdutwj6q915.execute-api.eu-west-2.amazonaws.com%2Fdev%2Fapi%2Fverify), and successfully logging in, will redirect you to:

```bash
/api/verify?code=<code>
```

This returns your token, which you can use in testing the authentication on the API. Use this token in the Authorization header to authenticate your requests.

The /api/verify route get's the client keys and redirect uri from the bucket.

