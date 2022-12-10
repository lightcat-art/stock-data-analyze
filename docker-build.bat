rem db를 build/run -> web을 build/run 각각 기동은 모두 됨. 네트워크 연결도 모두 되는디...?
docker compose run --service-ports -d db
docker compose run --service-ports -d web

rem 여전히 web network 가 연결되지 않음.
rem docker-compose build
rem docker-compose up -d rem 이 명령어로는 web app 이 기동되지 않음. 왜?
