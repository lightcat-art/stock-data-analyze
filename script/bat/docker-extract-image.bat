@echo off
rem 기반 이미지 추출
docker save -o stock-data-analyze-db.tar stock-data-analyze-db:latest
docker save -o stock-data-analyze-batch.tar stock-data-analyze-batch:latest


