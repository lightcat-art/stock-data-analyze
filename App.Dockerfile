FROM centos:8
# create working directory in docker
WORKDIR /home/stock
# setting envirionment
ENV DJANGO_DATABASE mysql-docker
#ENV DJANGO_DATABASE mysql-local

# use appstream repository
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Linux-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-Linux-*
#RUN useradd lightcat
#RUN passwd lightcat
#USER lightcat
#RUN dnf module -y install python38 #yum install로 처리.
#RUN alias python=python3 # alias가 먹히지 않음.
#RUN alias pip=pip3 # alias가 먹히지 않음.
RUN yum update -y
RUN yum install -y mariadb-devel gcc python38-devel
RUN pip3 list
RUN pip3 install --upgrade pip

# copy project
COPY . .
#RUN yum install -y libmysqlclient-dev
#RUN pip install --upgrade setuptools
# install dependencies
RUN pip3 install -r /home/stock/backend/requirements.txt

#RUN echo "python3 /home/stock/backend/manage.py makemigrations blog && python3 /home/stock/backend/manage.py migrate blog" > ./script/blog_db_init.sh
#RUN echo "python3 /home/stock/backend/manage.py makemigrations stocksimul && python3 /home/stock/backend/manage.py migrate stocksimul" > ./script/stocksimul_db_init.sh
#RUN echo "nohup python3 /home/stock/backend/manage.py runserver 0.0.0.0:8100 &" > ./script/django_server_start.sh
#RUN chmod +x ./script/*.sh

WORKDIR /shared

#COPY ./backend/dist/stock_data_analyze*.whl /root/
#RUN pip install /root/stock_data_analyze*.whl
#RUN find . -name 'stock_data_analyze*'
#RUN ["cd /root", "pip install stock_data_analyze*.whl"]

#RUN pip3 install virtualenv
#RUN virtualenv stock-data-analyze --python=python3.8
#RUN source stock-data-analyze/bin/activate

#RUN pip install stock_data_analyze-1.0.1-py3-none-any.whl

