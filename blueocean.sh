#!/bin/bash
## Script to auto-setup nginx reverse proxy with jenkins

# Initialize docker network
docker network create jenkins

## __Uncomment for docker-in-docker__
# docker run \
#   --name jenkins-docker \
#   --rm \
#   --detach \
#   --privileged \
#   --network jenkins \
#   --network-alias docker \
#   --env DOCKER_TLS_CERTDIR=/certs \
#   --volume jenkins-docker-certs:/certs/client \
#   --volume jenkins-data:/var/jenkins_home \
#   --publish 3000:3000 \
#   --publish 2376:2376 \
#   docker:dind \
#   --storage-driver overlay2 

## Build blueocean plug-in image
docker build -t myjenkins-blueocean:1.1 . 

## __Uncommenet for docker-in-docker__
# docker run \
#   --name jenkins-blueocean-dind \
#   --rm \
#   --detach \
#   --user root \
#   --network jenkins \
#   --env DOCKER_HOST=tcp://docker:2376 \
#   --env DOCKER_CERT_PATH=/certs/client \
#   --env DOCKER_TLS_VERIFY=1 \
#   --publish 8080:8080 \
#   --publish 50000:50000 \
#   --volume jenkins-data:/var/jenkins_home \
#   --volume jenkins-docker-certs:/certs/client:ro \
#   --volume "$HOME"/:/home \
#   myjenkins-blueocean:1.1 

## PUBLISH Jenkins 
## __Without nginx__
# docker run --name jenkins-blueocean-dofd --rm --detach -u root -v /var/run/docker.sock:/var/run/docker.sock -v jenkins-data:/var/jenkins_home -v "$HOME"/:/home --publish 8080:8080 myjenkins-blueocean:1.1

## __With nginx__ 
docker run \
  --name jenkins-blueocean-dofd  \
  --rm \
  --user root \
  --detach \
  --network jenkins \
  -v "$HOME"/jenkins-test:/var/jenkins_home/workspace/jenkins-test \
  -v "$HOME"/Team30-AY21:/var/jenkins_home/workspace/SecureGenericForum \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v jenkins-data:/var/jenkins_home \
  -e VIRTUAL_HOST=jenkins.justaforum.sitict.net \
  -e VIRTUAL_PORT=8080 \
  myjenkins-blueocean:1.1

## Publish nginx reverse proxu
docker run \
  --name nginx-rproxy \
  -d \
  --rm \
  --network jenkins \
  -u root \
  -p 443:443 \
  -p 8443:443 \
  -e HTTPS_PORT=443 \
  -v /var/run/docker.sock:/tmp/docker.sock:ro \
  -v "$HOME"/certs:/etc/nginx/certs \
  jwilder/nginx-proxy:0.9