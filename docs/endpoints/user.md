# User API

## Get User Information

`GET /api/v1/user`

Returns the email address of the authenticated user.

### Authorization

Requires a valid Cognito ID token in the Authorization header.

### Response

```json
{
    "email": "string"
}
```

### Error Responses

| Status Code | Description |
|--------|-------------|
| 404 | User not found |