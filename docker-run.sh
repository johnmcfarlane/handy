#!/usr/bin/env bash
set -e

docker run -it -v ~/.ssh:/root/.ssh -v ~/.ccache:/root/.ccache --name dev dev
