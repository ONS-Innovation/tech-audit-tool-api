# Tech Audit Tool API
This repository contains the infrastructure and 
code for deploying an API using Terraform on AWS.
The project is structured to support multiple environments.

This project is built using [Poetry](https://python-poetry.org/) for dependency management and [MkDocs](https://www.mkdocs.org/) for generating the documentation site.
The API Python code is built using [Flask Restx](https://flask-restx.readthedocs.io/en/latest/).

The API infrastructure is built using [Terraform](https://www.terraform.io/). The API Gateway available on AWS is used to handle the authentication and routing of requests to the Lambda function.

To deploy the API, the Terraform code is run to create the necessary resources on AWS. The Terraform code is located in the `terraform` directory. A certain pattern is to be followed when deploying a brand new API.

