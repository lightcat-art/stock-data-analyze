@echo off
rem db를 build/run -> web을 build/run 각각 기동은 모두 됨. 네트워크 연결도 모두 되는디...?
rem setx DJANGO_DATABASE "mysql-docker"
docker compose run --service-ports -d db
docker compose run --service-ports -d batch

rem docker compose build db
rem docker compose build web
