HOME=/home/ec2-user
sudo docker network create --ipam-driver default --subnet 172.21.0.10/16 --gateway 172.21.0.20 stock-data-analyze-default

sudo docker load -i ${HOME}/stock-data-analyze-db.tar
sudo docker load -i ${HOME}/stock-data-analyze-web.tar

sudo docker run -itd -p 4306:3306 --network stock-data-analyze-default --ip 172.21.0.30 --name stock-data-analyze-db stock-data-analyze-db:latest
mkdir django-volume
sudo docker run -itd -p 8100:8100 --network stock-data-analyze-default --ip 172.21.0.40 --volume ${HOME}/django-volume:/shared --name stock-data-analyze-web stock-data-analyze-web:latest



