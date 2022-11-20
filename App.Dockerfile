FROM centos:8
# create working directory in docker
WORKDIR docker-app
# use appstream repository
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Linux-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-Linux-*
#RUN useradd lightcat
#RUN passwd lightcat
#USER lightcat
RUN dnf module -y install python38
#RUN alias python=python3 # alias가 먹히지 않음.
#RUN alias pip=pip3 # alias가 먹히지 않음.
RUN pip3 list
RUN pip3 install --upgrade pip



COPY ./backend/dist/stock_data_analyze*.whl /root/
RUN pip install /root/stock_data_analyze*.whl
#RUN find . -name 'stock_data_analyze*'
#RUN ["cd /root", "pip install stock_data_analyze*.whl"]

#RUN pip3 install virtualenv
#RUN virtualenv stock-data-analyze --python=python3.8
#RUN source stock-data-analyze/bin/activate

#RUN pip install stock_data_analyze-1.0.1-py3-none-any.whl

