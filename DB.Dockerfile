FROM mysql:8.0.22
# 인코딩
ENV LC_ALL=C.UTF-8
ENV character-set-server utf8
ENV collation-server utf8_general_ci
ENV default-character-set utf8
ENV default-collation utf8_general_ci

# 스키마 명, 비밀번호
ENV MYSQL_DATABASE stock
ENV MYSQL_ROOT_PASSWORD root
#ENV MYSQL_USER stock
#ENV MYSQL_PASSWORD stock
#ENV MYSQL_ALLOW_EMPTY_PASSWORD true

ADD ./mysql-init-files /docker-entrypoint-initdb.d
EXPOSE 3306

# CMD 를 사용하면 명령을 한번 수행하고 종료되는 이미지를 생성하게 됨!
CMD ["mysqld"]
#CMD ["select * from user,host from user;"]
#ENTRYPOINT ["mysqld"]


#RUN mysql -u root -proot -e 'select user,host from user;'
#RUN create database stock character set utf8 collate utf8_general_ci;
#RUN create user 'stock'@'%' identified by 'stock';
#RUN grant all privileges on stock.* to 'stock'@'%';
#RUN grant all privileges on stock.* to 'stock'@'localhost';
#RUN flush all privileges;