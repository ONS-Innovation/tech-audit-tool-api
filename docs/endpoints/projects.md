# Projects API

## Get Projects

`GET /api/v1/projects`

Returns all projects associated with the authenticated user.

### Authorization

Requires a valid Cognito ID token in the Authorization header.

### Responses

| Status Code | Description                             |
|-------------|-----------------------------------------|
| 200         | Returns a list of project objects. |
| 401         | Authorization is required               |



## Create a Project

`POST /api/v1/projects`

Creates a new project.

### Authorization

Requires a valid Cognito ID token in the Authorization header.

### Request Body

```json
{
  "user": [
    {
      "email": "string",
      "roles": [
        "string"
      ],
      "grade": "string"
    }
  ],
  "details": [
    {
      "name": "string",
      "short_name": "string",
      "documentation_link": [
        "string"
      ],
      "project_description": "string"
    }
  ],
  "developed": [
    "string"
  ],
  "source_control": [
    {
      "type": "string",
      "links": [
        {
          "description": "string",
          "url": "string"
        }
      ]
    }
  ],
  "architecture": {
    "hosting": {
      "type": [
        "string"
      ],
      "details": [
        "string"
      ]
    },
    "database": {
      "main": [
        "string"
      ],
      "others": [
        "string"
      ]
    },
    "languages": {
      "main": [
        "string"
      ],
      "others": [
        "string"
      ]
    },
    "frameworks": {
      "main": [
        "string"
      ],
      "others": [
        "string"
      ]
    },
    "cicd": {
      "main": [
        "string"
      ],
      "others": [
        "string"
      ]
    },
    "infrastructure": {
      "main": [
        "string"
      ],
      "others": [
        "string"
      ]
    }
  },
  "stage": "string"
}
```

### Responses

| Status Code | Description                                             |
|-------------|---------------------------------------------------------|
| 201         | Created project. Returns the same project object as the request body.                                        |
| 401         | Authorization is required                              |
| 406         | Missing JSON data                                      |
| 409         | Project with the same name and owner already exists    |