#!/bin/bash

docker run -it --rm -v $(pwd):/opt --workdir /opt python:${1:-3.11}-slim bash
