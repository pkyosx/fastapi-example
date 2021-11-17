#!/bin/bash
docker-compose -p fastapi-sample-ut -f docker-compose/ut.yml build
docker-compose -p fastapi-sample-ap -f docker-compose/ap.yml up -d

echo "To run service, type the following command:"
echo "gunicorn main:app"

docker-compose -p fastapi-sample-ap -f docker-compose/ap.yml exec ap-service /bin/bash