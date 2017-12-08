.PHONY: app clean push

TRAVIS_BUILD_NUMBER ?= none

clean:
	rm -rf pyslackers_website/static/dist/ node_modules/

# Build the client inside a docker container vs requiring node on the host
pyslackers_website/static/dist/:
	docker run \
		--rm -it -v ${PWD}:/app \
		--workdir /app --user ${UID}:${GID} \
		node:8.9-alpine \
		sh -c 'npm i -g yarn \
			&& yarn install \
			&& yarn run lint \
			&& yarn run build'

client: pyslackers_website/static/dist/

app: pyslackers_website/static/dist/
	docker build \
		-t pyslackers/website:latest \
		-t pyslackers/website:$(TRAVIS_BUILD_NUMBER) \
		.

push: app
	docker push pyslackers/website:latest
	docker push pyslackers/website:$(TRAVIS_BUILD_NUMBER)
