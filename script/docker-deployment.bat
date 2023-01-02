@echo off

rem create entwork
docker network create --ipam-driver default --subnet 172.21.0.10/16 --gateway 172.21.0.20 stock-data-analyze-default
rem load image
docker load -i stock-data-analyze-db.tar
docker load -i stock-data-analyze-web.tar

rem run db&app
docker run -itd -p 4306:3306 --network stock-data-analyze-default --ip 172.21.0.30 --name stock-data-analyze-db stock-data-analyze-db:latest
docker run -itd -p 8100:8100 --network stock-data-analyze-default --ip 172.21.0.40 --name stock-data-analyze-web stock-data-analyze-web:latest


