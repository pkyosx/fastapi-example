# If you run into questions when adopting fastapi
- [Q1] How to customize our input schema error (status_code=422)
- [Q2] How to generate error response for openapi in a clean way
- [Q3] How to define a property that can be string or null in openapi
- [Q4] How to do if I want schema to be inheritable but don't want child class to overwrite parent's any attributes
- [Q5] How to get '/path/{param}' in the middleware for metrics
- [Q6] How to print request body when error happends
- [Q7] How to print the entire exception chain when wanted
- [Q8] How to create log context and add trace id into it

You can search the above question in source code for the answers. (ex. search "[Q1]")

# In this example we have
- A login method for all users
- A JWT token for authorization that can be set on swagger UI
- Two different roles (user, admin)
- One read messages API for user
- One leave message API for admin
- Generate response automatically from Errors


# How to run local test
Install [docker-compose](https://docs.docker.com/compose/install/) before continue the following step.

This will build container
```
make build
```

This will start the server on http://localhost:9999 you can find the api doc on http://localhost:9999/api_doc/swagger
```
make up FASTAPI_EXAMPLE_PORT=9999
```

This will help you get into the server shell
```
make attach
```

You can run the unit test
```
make test
```

To tear down all the resource
```
make down
```

# How to change code
Install [pre-commit](https://pre-commit.com/) to align the code formatting

Enable pre-commit and you are good to go
```
pre-commit install
```
