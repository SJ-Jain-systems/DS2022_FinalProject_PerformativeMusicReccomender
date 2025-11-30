#!/usr/bin/env bash
set -e

docker build -t mini-music-recommender:latest .
docker run --rm -p 8080:8080 --env-file .env mini-music-recommender:latest
