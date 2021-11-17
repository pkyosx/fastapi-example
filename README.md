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
This will build container and lead you into container's shell
```
./setup_ut.sh
```

Type following command inside container will trigger UT
```
pip install -r requirements-test.txt
pytest --log-level=INFO --sw tests/
```

Type following command inside container will start up a server on localhost:8888
```
gunicorn main:app
```

```
visit: http://localhost:8888/api_doc/swagger
```

To remove the container
```
./teardown_ut.sh
```