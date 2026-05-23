#!/bin/bash
cd $(dirname "$0")

podman-compose up --build
