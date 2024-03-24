#!/bin/bash

docker build -t planes-segmentation-app:latest .

xhost +local:

docker run --rm -it -e DISPLAY=unix$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix planes-segmentation-app:latest
