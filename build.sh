#!/usr/bin/env bash

git pull

# remove container 
docker rm $(docker stop btc-monitor-container)

# build docker image
docker build -t btc-monitor .

# run
# docker run -d --name btc-monitor-container -e TZ=Asia/Seoul -v $(pwd)/config:/app/config btc-monitor
docker run -d --tty --name btc-monitor-container --memory=1g -e TZ=Asia/Seoul -v $(pwd)/config:/app/config btc-monitor
# config autostart
docker update --restart unless-stopped $(docker ps -q)

# remove docker old image
docker image prune -f

# check status
docker ps
