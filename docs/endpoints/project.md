# Projects API

## Get All Projects

`GET /api/v1/project/{project_name}`

Returns the project associated with the authenticated user.

### Authorization

Requires a valid Cognito ID token in the Authorization header.

### Responses

| Status Code | Description                             |
|-------------|-----------------------------------------|
| 200         | Returns a project object. |
| 401         | Authorization is required               |
| 404         | Project not found                       |


## Update a Project

`PUT /api/v1/projects`

Updates a project.

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

| Status Code | Description                             |
|-------------|-----------------------------------------|
| 200         | Returns the same project object as the request body. |
| 401         | Authorization is required               |
| 404         | Project not found                       |
| 406         | Missing JSON data                       |