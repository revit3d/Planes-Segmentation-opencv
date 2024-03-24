#!/bin/bash

docker build -t planes-segmentation-app:latest .

docker run --rm -it planes-segmentation-app:latest
