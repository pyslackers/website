.PHONY: app clean push

# available config via envvars
TRAVIS_BUILD_NUMBER ?= none

# consts
IMAGE_NAME = pyslackers/website

clean:
	rm -rf app/static/dist/ node_modules/

# Build the client inside a docker container vs requiring node on the host
app/static/dist/:
	docker run \
		--rm -it -v ${PWD}:/app \
		--workdir /app --user ${UID}:${GID} \
		node:8.9-alpine \
		sh -c 'npm i -g yarn \
			&& yarn install \
			&& yarn run lint \
			&& yarn run build:prod'

client: app/static/dist/

app: app/static/dist/
	docker build \
		-t $(IMAGE_NAME):latest \
		-t $(IMAGE_NAME):$(TRAVIS_BUILD_NUMBER) \
		.

push: app
	docker push $(IMAGE_NAME):latest
	docker push $(IMAGE_NAME):$(TRAVIS_BUILD_NUMBER)
