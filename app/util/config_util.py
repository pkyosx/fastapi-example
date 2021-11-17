# This is just an easy interface. In real-world, you might want to
# read config from files and encrypt credential in it.

class Config:
    auth_secret_key = "access-token-secret"
    auth_token_exp = 86400
    auth_users = {
        "user1": "user_password1"
    }
    auth_admins = {
        "admin1": "admin_password1"
    }