@echo off

if "%1"=="pre" goto pre_commit
if "%1"=="build_docker" goto build_docker
if "%1"=="run_docker" goto run_docker

echo Unknown command: %1
goto end

:pre_commit
pre-commit run --all-files
goto end

:build_docker
docker build -t muvistat .
goto end

:run_docker
:: run docker detached and map port 8000 to 8000
docker run -d -p 8000:8000 --name muvistat muvistat
echo Docker container is running. Access the app at http://localhost:8000
echo See http://localhost:8000/docs for API documentation.
goto end

:end
