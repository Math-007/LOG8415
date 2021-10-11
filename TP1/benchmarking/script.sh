#!/bin/bash
# Execute and show results of your benchmarking

echo "Building docker container"
docker build -t log8415/tp1-benchmarking:latest .

echo "Running docker container"
docker run -it \
    -v ./img/:/app/img \
    -v $HOME/.aws/credentials:/root/.aws/credentials:ro \
    log8415/tp1-benchmarking:latest

echo "Results can be found in benchmarking/img/"