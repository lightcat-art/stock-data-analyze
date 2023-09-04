@echo off

rem create entwork
docker network create --ipam-driver default --subnet 172.21.0.10/16 --gateway 172.21.0.20 stock-data-analyze-default
rem load image
docker load -i stock-data-analyze-db.tar
docker load -i stock-data-analyze-batch.tar

rem run db&app
docker run -itd -p 4306:3306 --network stock-data-analyze_network-default --ip 172.21.0.30 --name stock-data-analyze-db stock-data-analyze-db:latest
docker run -itd -p 8100:8100 --network stock-data-analyze_network-default --ip 172.21.0.40 --entrypoint /bin/bash --name stock-data-analyze-batch stock-data-analyze-batch:latest start.sh


