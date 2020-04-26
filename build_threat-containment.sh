#!/bin/bash
docker build --no-cache --network=host --tag=threat_containment:v0.1 -f threat-containment/Dockerfile .
