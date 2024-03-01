.PHONY: reset test-all package-test run-notebooks run-notebooks-dev docker-test-all docker-test-all-python-oldest-stable docker-test-all-python-latest-stable docker-test-all-python-rc docker-test-all-solo

PY_VERSION_BASELINE=3.8
PY_VERSION_STABLE=3.11
PY_VERSION_LATEST=3.12
TESTING_IMAGE_NAME=dnastack/client-library-testing

run-notebooks:
	docker run -it --rm \
		-v $$(pwd)/samples:/workspace \
		--workdir /workspace \
		-p 8888:8888 \
		jupyter/scipy-notebook

run-notebooks-dev:
	docker run -it --rm \
		-v $$(pwd)/samples:/workspace \
		-v $$(pwd)/:/opt/src \
		--workdir /workspace \
		-p 8888:8888 \
		jupyter/scipy-notebook

reset:
	rm -rf ~/.dnastack/config.yaml
	rm ~/.dnastack/sessions/* 2> /dev/null

test-all:
	E2E_ENV_FILE=.env ./scripts/run-e2e-tests.sh

package-test:
	mkdir -p dist; rm dist/*; ./scripts/build-package.py --pre-release a
	docker run -it --rm \
		-v $$(pwd)/dist:/dist-test \
		--workdir /dist-test \
		python:$(PY_VERSION_BASELINE)-slim \
		bash -c "pip install *.whl && dnastack use --no-auth viral.ai"

docker-test-all: docker-test-all-python-oldest-stable docker-test-all-python-latest-stable docker-test-all-python-rc

# Testing the oldest stable version.
docker-test-all-baseline:
	make TESTING_PYTHON=python:$(PY_VERSION_BASELINE)-slim WEBDRIVER_DISABLED=false docker-test-all-solo

# Testing the latest stable version.
docker-test-all-stable:
	make TESTING_PYTHON=python:$(PY_VERSION_STABLE)-slim WEBDRIVER_DISABLED=false docker-test-all-solo

# Testing the release candidate version.
docker-test-all-latest:
	make TESTING_PYTHON=python:$(PY_VERSION_LATEST)-slim WEBDRIVER_DISABLED=false docker-test-all-solo

# Testing the anaconda release.
docker-test-all-anaconda:
	make TESTING_PYTHON=continuumio/miniconda3 WEBDRIVER_DISABLED=false docker-test-all-solo

docker-test-all-pypy:
	make TESTING_PYTHON=pypy WEBDRIVER_DISABLED=false docker-test-all-solo

docker-test-all-solo:
	./scripts/run-e2e-tests-locally-in-docker.sh $(TESTING_PYTHON) $(WEBDRIVER_DISABLED)

#	cat Dockerfile-template | PY_VERSION=$(TESTING_PYTHON) envsubst
#	docker build -t $(TESTING_IMAGE_NAME):python-$(TESTING_PY_VERSION) -f Dockerfile-$(TESTING_PY_VERSION) .
#	docker run -it --rm $(TESTING_IMAGE_NAME):python-$(TESTING_PY_VERSION)
#	docker rmi $(TESTING_IMAGE_NAME):python-$(TESTING_PY_VERSION)
