@echo off

if "%1"=="pre" goto pre_commit
if "%1"=="run_dev" goto run_dev
if "%1"=="build_docker" goto build_docker
if "%1"=="run_docker" goto run_docker

echo Unknown command: %1
goto end

:pre_commit
pre-commit run --all-files
goto end

:run_dev
:: run the app locally in dev mode
fastapi dev app/main.py
goto end

:build_docker
:: build docker image, named "muvistat"
docker build -t muvistat .
goto end

:run_docker
:: check if container still running
docker ps -q --filter "name=muvistat" | findstr . >nul
if %errorlevel%==0 (
    echo Container muvistat is already running. Stopping and removing it...
    docker stop muvistat
    docker rm muvistat
    )
:: run docker detached (free terminal) and map external to internal port 8000
docker run -d -p 8000:8000 --name muvistat muvistat
echo Docker container is running. Access the app at http://localhost:8000
echo See http://localhost:8000/docs/ for API documentation.
goto end

:end
