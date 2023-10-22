# This is just an easy interface. In real-world, you might want to read config from files and encrypt credential in it.

import os


class Config:
    app_title = "fastapi-example"
    app_description = "This is a sample fastapi web app"
    app_version = "1.0"
    auth_secret_key = "access-token-secret"
    auth_token_exp = 86400
    auth_users = {"user1": "user_password1"}
    auth_admins = {"admin1": "admin_password1"}
    sqlalchemy_database_url = os.environ["SQLALCHEMY_DATABASE_URL"]
