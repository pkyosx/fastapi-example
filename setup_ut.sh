#!/bin/bash
docker-compose -p fastapi-sample-ut -f docker-compose/ut.yml build
docker-compose -p fastapi-sample-ut -f docker-compose/ut.yml up -d

echo "To run all test: (run the following command)"
echo pip install -r requirements-test.txt
echo pytest --log-level=INFO --sw tests/

docker-compose -p fastapi-sample-ut -f docker-compose/ut.yml exec ut-service /bin/bash