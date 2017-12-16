#!/usr/bin/env bash

echo "Pushing image to Docker Hub"
docker login -u="${DOCKER_USERNAME}" -p="${DOCKER_PASSWORD}"
make push

echo "Preparing for deploy"
cd ansible
pip install ansible

openssl aes-256-cbc -K $encrypted_f5552f32211c_key -iv $encrypted_f5552f32211c_iv -in id_rsa.enc -out id_rsa -d
chmod 600 id_rsa

ansible-galaxy install -r requirements.yml

echo -n "$ANSIBLE_PASSWORD" > .pass

ansible-playbook \
    playbook.yml \
    --private-key=id_rsa \
    --tags="deploy" \
    --extra-vars "deploy_version=${TRAVIS_BRANCH}"
