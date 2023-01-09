docker --version || RES=$?

echo "Docker version response = ${RES}"

if [ "${RES}" != "" ]
then
	echo "Docker does not installed."
	echo "Start installing docker."
	sudo yum -y update
	sudo yum install -y yum-utils	
	sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
	sudo yum install -y docker-ce docker-ce-cli containerd.io
	sudo systemctl start docker
	sudo systemctl enable docker

	docker --version || RES=$?
	echo "Docker re-verify version response = ${RES}"
else
	echo "Docker already installed."
fi
