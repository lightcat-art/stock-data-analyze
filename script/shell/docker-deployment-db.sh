#HOME은 보통 linux에 default로 설정되어 있음.
#HOME=/home/ec2-user
sudo docker network create --ipam-driver default --subnet 172.21.0.10/16 --gateway 172.21.0.20 stock-data-analyze_network-default

sudo docker load -i ${HOME}/stock-data-analyze-db.tar

sudo docker run -itd -p 4306:3306 --network stock-data-analyze_network-default -v db-volume:/var/lib/mysql --ip 172.21.0.30 --name stock-data-analyze-db stock-data-analyze-db:latest



