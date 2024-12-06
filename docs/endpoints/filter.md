# Filter API

## Filter Projects

`GET /api/v1/projects/filter`

Filter projects based on multiple criteria.

### Query Parameters

| Parameter | Description |
|-----------|-------------|
| email | User email to filter by (comma-separated) |
| roles | Roles to filter by (comma-separated) |
| name | Project name to filter by (comma-separated) |
| developed | Filter by development type ("In house", "Partnership", "Outsourced") |
| languages | Programming languages to filter by (comma-separated) |
| source_control | Source control systems to filter by (comma-separated) |
| hosting | Hosting platforms to filter by (comma-separated) |
| database | Database types to filter by (comma-separated) |
| frameworks | Frameworks to filter by (comma-separated) |
| cicd | CI/CD tools to filter by (comma-separated) |
| infrastructure | Infrastructure tools to filter by (comma-separated) |
| return | Sections to return in response (user, details, developed, source_control, architecture) |

### Responses

| Status Code | Description                             |
|-------------|-----------------------------------------|
| 200         | Returns filtered list of projects matching the specified criteria. If the `return` parameter is specified, only the requested sections will be included in the response. |
| 401         | Authorization is required               |
| 404         | Project not found                       |
