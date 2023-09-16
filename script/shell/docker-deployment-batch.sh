#HOME은 보통 linux에 default로 설정되어 있음.
#HOME=/home/ec2-user
#sudo docker network create --ipam-driver default --subnet 172.21.0.10/16 --gateway 172.21.0.20 stock-data-analyze_network-default

sudo docker load -i ${HOME}/stock-data-analyze-batch.tar

if [ ! -d ${HOME}/django-volume ]; then
 mkdir ${HOME}/django-volume
else
 echo "${HOME}/django-volume exists"
fi

sudo docker run -itd -p 8100:8100 --network stock-data-analyze_network-default --ip 172.21.0.40 --entrypoint /bin/bash --volume ${HOME}/django-volume:/shared --name stock-data-analyze-batch stock-data-analyze-batch:latest start.sh



