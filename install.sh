#!/bin/sh

apt-get update

apt-get -y install python3-pip docker.io

pip3 -H install pandas twitter ruamel.yaml

# Install Docker Compose
curl -L https://github.com/docker/compose/releases/download/1.19.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Copy config.yaml.sample to config.yaml and delete the sample
cp dags/config/config.yaml.sample dags/config/config.yaml && rm dags/config/config.yaml.sample
