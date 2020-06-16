#/bin/bash
docker build --tag=headpage:latest .
docker run -d --rm -p 8000:8000 --name headpage headpage:latest
# If you have access to CloudOne Application security
#docker run -d --rm -p 8000:8000 --name headpage -e TREND_AP_KEY=<KEY> -e TREND_AP_SECRET=<SECRET> headpage:latest