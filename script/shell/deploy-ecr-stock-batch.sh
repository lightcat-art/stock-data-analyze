sudo docker pull ${AWS_ECR_REGISTRY}/stock-data-analyze-batch:latest

#checking just stopped container using ps -a
IS_GREEN=$(sudo docker ps -a | grep stock-data-analyze-batch-green)
IMG_GREEN=stock-data-analyze-batch-green
IMG_BLUE=stock-data-analyze-batch-blue
if [ -z "$IS_GREEN" ];then # when blue
        echo "### BLUE => GREEN ###"
        sudo docker tag ${AWS_ECR_REGISTRY}/stock-data-analyze-batch:latest ${IMG_GREEN}:latest

#        if [ -d ${HOME}/django-volume/green ]; then
#                rm -r ${HOME}/django-volume/green/*
#                echo "1. clear green file"
#        fi

        sudo docker run -itd -p 8100:8100 --env-file .env -v ${HOME}/django-volume/green/shared:/shared --network stock-data-analyze_network-default --ip 172.21.0.40 --entrypoint /bin/bash --name ${IMG_GREEN} ${IMG_GREEN}:latest start.sh

        while [ 1 = 1 ];do
                echo "2. green health check "
                sleep 3
		#curl -sSf http://127.0.0.1:8100/stocksimul/healthcheck || RES=$?
		RES=$(curl -sSf http://127.0.0.1:8100/stocksimul/healthcheck)

                if [ "$RES" == '"success"' ];then
                        echo "health check success"
			break
                fi
        done
	sudo docker stop ${IMG_BLUE}
	sudo docker rm ${IMG_BLUE}
else
        echo "### GREEN => BLUE ###"
        sudo docker tag ${AWS_ECR_REGISTRY}/stock-data-analyze-batch:latest ${IMG_BLUE}:latest

#        if [ -d ${HOME}/django-volume/blue ]; then
#                rm -r ${HOME}/django-volume/blue/*
#                echo "1. clear blue file"
#        fi

        sudo docker run -itd -p 8101:8100 --env-file .env -v ${HOME}/django-volume/blue/shared:/shared --network stock-data-analyze_network-default --ip 172.21.0.41 --entrypoint /bin/bash --name ${IMG_BLUE} ${IMG_BLUE}:latest start.sh

        while [ 1 = 1 ];do
                echo "2. blue health check "
                sleep 3
                #curl -sSf http://127.0.0.1:8101/stocksimul/healthcheck || RES=$?
		RES=$(curl -sSf http://127.0.0.1:8101/stocksimul/healthcheck)

                if [ "$RES" == '"success"' ];then
                        echo "health check success"
			break
                fi
        done
	sudo docker stop ${IMG_GREEN}
	sudo docker rm ${IMG_GREEN}
fi
