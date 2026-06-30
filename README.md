# muvistat

Get, track, and analyse view, like, and comment count of YouTube videos.

## Goal
Mainly, this is a project to improve my software engineering skills and to learn more about
- SQLite,
- HTTP,
- fastAPI,
- interaction with third-party APIs,
- and Docker.

Also, I am a classical musician with some music videos on different (not only my own) YouTube channels, so this might be fun to run regularely and see how the statistics develop over time (I love statistics!) ;)

## How to use (development stage)
### Installation for development
1. Install Python (at least 3.9), git, and pip if not already satisfied.
2. Clone the repository `git clone https://github.com/karlhaensel/muvistat.git`
3. Install venv with `python -m venv .venv` and activate it:
    - Windows: `.venv\Scripts\activate.bat` (cmd) or `.venv\Scripts\Activate.ps1` (PowerShell)
    - Linux: `source .venv/bin/activate`
4. Install dependencies with `pip install -r requirements.txt`
5. Create an `.env` file in the root directory according to the `.env.example` file and fill in your YouTube API key.

### Running for development
1. Run the script with `fastapi dev app/main.py` or run `.\make.bat run_dev` (Windows)
2. Follow the link in terminal to open the Swagger UI and test the API endpoints.

### Running with Docker
1. Make sure, you have Docker installed and running.
2. Build the Docker image with `docker build -t muvistat .`
3. Run the Docker container with `docker run -p 8000:8000 --name muvistat muvistat`
4. Follow the link in terminal to open the Swagger UI and test the API endpoints.
You can also use `.\make.bat build_docker` and `.\make.bat run_docker` to build and run the Docker container on Windows.

## Stage of development
- [x] basic database setup with SQLite
- [x] pydantic models for API
- [x] fastAPI endpoints for adding videos and snapshots of their statistics (automatic documentation with Swagger UI)
- [ ] fetching statistics from YouTube API
- [ ] client for API including basic statistics
- [ ] "alerts" for videos that have a significant change in statistics
- [ ] ...
