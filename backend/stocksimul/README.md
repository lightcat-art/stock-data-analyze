# 프로젝트 구성 방법

### 1. Python / pip version
* python >= 3.7
* python 3.8 버전에서는 ruamel.yaml.clib==0.2.6B 가 아닌 ruamel.yaml.clib==0.2.6 로 설치해야함.

### 2. MySQL DB 생성
```doctest
create database stock character set utf8 collate utf8_general_ci;
create user 'stock'@'%' identified by 'stock';
grant all privileges on stock.* to 'stock'@'localhost';
```

### 3. DB initialize & runserver
```doctest
# manage.py 경로 진입
python manage.py makemigrations [app]
python manage.py migrate [app]
# run django
python manage.py runserver [port]
```
