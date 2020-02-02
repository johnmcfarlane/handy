#!/usr/bin/env bash
set -e

docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
