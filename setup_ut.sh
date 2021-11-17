#!/bin/bash +ex
docker-compose -p fastapi-sample -f docker-compose/ut.yml build
docker-compose -p fastapi-sample -f docker-compose/ut.yml up -d

echo "============================================="
echo "To run all test: (run the following command)"
echo "============================================="
echo pip install -r requirements-test.txt
echo pytest --log-level=INFO --sw tests/
echo "============================================="
echo
echo "================================================="
echo "To run local service: (run the following command)"
echo "================================================="
echo gunicorn main:app
echo "================================================="

docker-compose -p fastapi-sample -f docker-compose/ut.yml exec ut-service /bin/bash