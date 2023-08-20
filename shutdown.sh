docker stop $(docker ps -aq);

docker rm $(docker ps -aq);

docker volume rm database;

docker network rm general-network;