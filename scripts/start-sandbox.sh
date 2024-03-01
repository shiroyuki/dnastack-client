#!/bin/bash

docker run -it --rm -v $(pwd):/opt --workdir /opt python:3-slim bash
