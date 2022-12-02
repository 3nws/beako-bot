#!/bin/bash

docker build -t beako .
docker run -d -it --network="host" --rm --name beako-run beako