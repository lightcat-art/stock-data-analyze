@echo off
rem 기반 이미지 추출
docker save -o stock-data-analyze-db.tar stock-data-analyze-db:latest
docker save -o stock-data-analyze-web.tar stock-data-analyze-web:latest


