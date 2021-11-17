# This example show you some practice you might need
- [ ] How to customize our input schema error (status_code=422)
- [ ] How to generate error response for openapi in a clean way
- [ ] How to define a property that can be string or null in openapi
- [ ] How to do if I want schema to be inheritable but don't want child class to overwrite parent's any attributes
- [ ] How to get '/path/{param}' in the middleware for metrics
- [ ] How to print request body when error happends
- [ ] How to print the entire exception chain when wanted


# How to run local test

This will build container and lead you into container's shell
```
./setup_ut.sh
```

Type following command inside container
```
pip install -r requirements-test.txt
pytest --log-level=INFO --sw tests/
```

# How to run local server

This will build container and lead you into container's shell
```
./setup_ap.sh
```

Type following command inside container
```
gunicorn main:app
```

visit: http://localhost:8888/api_doc/swagger