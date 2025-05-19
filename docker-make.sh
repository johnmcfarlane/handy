#!/usr/bin/env bash
set -e

docker build --tag dev ~/bin
docker create -t --name dev -i dev
