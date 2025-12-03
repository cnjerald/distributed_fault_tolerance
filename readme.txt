YOU MUST DOWNLOAD POSTGRES
https://www.postgresql.org/download/
SET PASSWORD TO 1234

on THIS PATH add THIS
C:\Program Files\PostgreSQL\17\data\pg_hba.conf
host  all  all  172.25.0.0/16  md


INSTALL DOCKER!
https://www.docker.com/products/docker-desktop/

docker network create --subnet=172.25.0.0/16 schoolnet
docker network ls
docker-compose build
docker-compose up -d