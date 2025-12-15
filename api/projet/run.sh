#!/bin/bash

# Script pour build et run Magik Swipe

if [ "$1" == "build" ]; then
    docker build -t magik-swipe .
elif [ "$1" == "run" ]; then
    shift  # Remove 'run' from args
    if [ "$1" == "--interactive" ]; then
        shift
        theme="$1"
        shift
        extra_args="$@"
        TOKEN=$(grep REPLICATE_API_TOKEN $(pwd)/../.env | sed 's/.*=//' | tr -d "'\"")
        docker run -it -v $(pwd)/univers:/app/univers -e REPLICATE_API_TOKEN="$TOKEN" --rm magik-swipe bash -c "python main.py --theme '$theme' $extra_args && bash"
    else
        theme="$1"
        shift
        extra_args="$@"
        TOKEN=$(grep REPLICATE_API_TOKEN $(pwd)/../.env | sed 's/.*=//' | tr -d "'\"")
        docker run -v $(pwd)/univers:/app/univers -e REPLICATE_API_TOKEN="$TOKEN" magik-swipe python main.py --theme "$theme" $extra_args
    fi
else
    echo "Usage: ./run.sh build"
    echo "       ./run.sh run <theme> [options]"
    echo "       ./run.sh run --interactive <theme> [options]"
    echo "Options: --words-only, --images-only, --videos-only"
fi