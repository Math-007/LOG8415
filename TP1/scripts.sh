#!/bin/bash
# Execute and show results of your benchmarking

echo "Building docker container"
docker build -t log8415/tp1-benchmarking:latest -f benchmarking/Dockerfile benchmarking

echo "Running docker container with benchmark program"
docker run -it \
    # Mount volume to save the graphs
    -v $(pwd)/benchmarking/img/:/app/img \
    # Mount host system aws credentials
    -v $HOME/.aws/credentials:/root/.aws/credentials:ro \
    log8415/tp1-benchmarking:latest

echo "Results can be found in benchmarking/img/"