docker volume create database;
docker network create general-network;
docker run --name translation-db -d -v database:/var/lib/postgresql/data/ --env-file .env.db --network general-network postgres:13.0-alpine;

docker build -t translation-app .;

docker run --rm --gpus all -p 8000:8000 --env-file .env -v $(pwd):/translation-app --network general-network translation-app /bin/bash ./setup.sh;