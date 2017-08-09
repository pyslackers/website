#!/usr/bin/env bash

echo "Pushing image to Docker Hub"
docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
docker push pyslackers/website:latest
docker push pyslackers/website:$TRAVIS_BUILD_NUMBER

# TODO: update ansible to use the pushed images...

echo "Running deployment to server"
cd ansible
ansible-galaxy install -r requirements.yml

echo -n "$ANSIBLE_PASSWORD" > ./.pass

ansible-playbook playbook.yml --tags "deploy"