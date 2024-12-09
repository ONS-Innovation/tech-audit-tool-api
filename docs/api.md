# API Documentation

The Tech Audit Tool API provides endpoints for managing project data and authentication. All endpoints require authentication using AWS Cognito ID tokens.

## Interactive API Documentation

<iframe src="https://tech-audit-tool-api.sdp-dev.aws.onsdigital.uk/" width="100%" height="800px" frameborder="0"></iframe>


## Authentication

All API endpoints require a valid AWS Cognito ID token in the Authorization header:

```
Authorization: <id_token>
```

## Base URL

All endpoints are prefixed with `/api/v1/` as the namespace.

## Available Endpoints

- [Authentication](endpoints/auth.md)
    - Verify tokens
    - Refresh tokens
[Projects](endpoints/projects.md)
    - Get all projects
    - Create new project
    - Get project details
    - Update project
- [User](endpoints/user.md)
    - Get user information
- [Filters](endpoints/filter.md)
    - Filter projects by criteria