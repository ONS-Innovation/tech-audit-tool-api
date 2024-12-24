from flask_restx import fields


# Had problems with initialising this as 'ns' wouldn't have been initialised so it would fail.
# Making this a function would the model to intialised when it's used and when 'ns' has been initialised.
def get_project_model():
    from .resources import ns

    user_model = ns.model(
        "User",
        {
            "email": fields.String(required=True, description="User email"),
            "roles": fields.List(
                fields.String, required=True, description="Roles of the user"
            ),
            "grade": fields.String(required=False, description="Grade of the user"),
        },
    )

    details_model = ns.model(
        "Details",
        {
            "name": fields.String(required=True, description="Project name"),
            "short_name": fields.String(
                required=True, description="Short name of the project"
            ),
            "documentation_link": fields.List(
                fields.String,
                required=False,
                description="Link to the project documentation",
            ),
            "project_description": fields.String(
                required=False, description="Description of the project"
            ),
        },
    )

    source_control_model = ns.model(
        "SourceControl",
        {
            "type": fields.String(required=True, description="Type of source control"),
            "links": fields.List(
                fields.Nested(
                    ns.model(
                        "RepoLink",
                        {
                            "description": fields.String(
                                required=True,
                                description="Description of the repository link",
                            ),
                            "url": fields.String(
                                required=True, description="URL of the repository link"
                            ),
                        },
                    )
                ),
                required=True,
                description="Links to repositories",
            ),
        },
    )

    architecture_model = ns.model(
        "Architecture",
        {
            "hosting": fields.Nested(
                ns.model(
                    "Hosting",
                    {
                        "type": fields.List(
                            fields.String, required=True, description="Type of hosting"
                        ),
                        "details": fields.List(
                            fields.String,
                            required=False,
                            description="Other hosting types",
                        ),
                    },
                )
            ),
            "database": fields.Nested(
                ns.model(
                    "Database",
                    {
                        "main": fields.List(
                            fields.String, required=False, description="Main database"
                        ),
                        "others": fields.List(
                            fields.String, required=True, description="Other databases"
                        ),
                    },
                )
            ),
            "languages": fields.Nested(
                ns.model(
                    "Languages",
                    {
                        "main": fields.List(
                            fields.String, required=False, description="Main language"
                        ),
                        "others": fields.List(
                            fields.String, required=True, description="Other languages"
                        ),
                    },
                )
            ),
            "frameworks": fields.Nested(
                ns.model(
                    "Frameworks",
                    {
                        "main": fields.List(
                            fields.String, required=False, description="Main framework"
                        ),
                        "others": fields.List(
                            fields.String,
                            required=True,
                            description="Other frameworks",
                        ),
                    },
                )
            ),
            "cicd": fields.Nested(
                ns.model(
                    "cicd",
                    {
                        "main": fields.List(
                            fields.String, required=False, description="Main CICD tool"
                        ),
                        "others": fields.List(
                            fields.String,
                            required=True,
                            description="Other CICD tools",
                        ),
                    },
                )
            ),
            "infrastructure": fields.Nested(
                ns.model(
                    "Infrastructure",
                    {
                        "main": fields.List(
                            fields.String,
                            required=False,
                            description="Main infrastructure tool",
                        ),
                        "others": fields.List(
                            fields.String,
                            required=True,
                            description="Other infrastructure tools",
                        ),
                    },
                )
            ),
        },
    )

    supporting_tools_model = ns.model(
        "SupportingTools", 
        {
            "code_editors": fields.List(
                fields.String, required=True, description="Code editors"
            ),
            "ui_tools": fields.List(
                fields.String, required=True, description="UI tools"
            ),
            "diagram_tools": fields.List(
                fields.String, required=True, description="Diagram tools"
            ),
            "project_tracking_tools": fields.List(
                fields.String, required=True, description="Project tracking tools"
            ),
            "documentation_tools": fields.List(
                fields.String, required=True, description="Documentation tools"
            ),
            "communication_tools": fields.List(
                fields.String, required=True, description="Communication tools"
            ),
            "collaboration_tools": fields.List(
                fields.String, required=True, description="Collaboration tools"
            ),
            "incident_management": fields.String(
                required=True, description="Incident management tools"
            )

        }
    )

    project_model = ns.model(
        "Project",
        {
            "user": fields.List(
                fields.Nested(user_model), required=True, description="List of users"
            ),
            "details": fields.List(
                fields.Nested(details_model),
                required=True,
                description="Details of project",
            ),
            "developed": fields.List(
                fields.Raw, required=True, description="Development details"
            ),
            "source_control": fields.List(
                fields.Nested(source_control_model),
                required=True,
                description="Source control platforms",
            ),
            "architecture": fields.Nested(
                architecture_model, required=True, description="Architecture details"
            ),
            "stage": fields.String(
                required=True, description="Stage status of the project"
            ),
            "supporting_tools": fields.Nested(
                supporting_tools_model, required=True, description="Supporting Tools Details"
            ),
        },
    )

    return project_model


def get_refresh_model():
    from .resources import ns

    refresh_model = ns.model(
        "Refresh",
        {"refresh_token": fields.String(required=True, description="Refresh token")},
    )
    return refresh_model
