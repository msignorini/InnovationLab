#!/bin/bash
#docker build --no-cache --network=host --tag=threat_containment:v0.1 .
docker build --no-cache --network=host --tag=lab_manager:v0.1 -f lab-manager/Dockerfile .
