# Authentication

The API uses AWS Cognito for authentication. All API endpoints require a valid ID token in the Authorization header.

## Verify Token

`GET /api/v1/verify`

Exchange authorization code for tokens.

### Query Parameters

| Parameter | Description |
|-----------|-------------|
| code | Authorization code from Cognito callback |

### Responses

| Status Code | Description |
|-----------|-------------|
| 200 | Success. Response body contains the new ID token: `{"id_token": "<id_token>", "refresh_token": "<refresh_token>"}`. |
| 400 | Bad Request |