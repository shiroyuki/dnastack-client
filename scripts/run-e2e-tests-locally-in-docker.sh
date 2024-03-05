# Create the test image for testing in isolation.
#
# Please note that the testing will be done on x86-64 due to the compatibility issue with Chrome for Testing.

set -e

export PYTHON_IMAGE=${1}
export WEBDRIVER_DISABLED=${2}
export TEST_CMD=${3}
export TEST_IMAGE_VERSION=$(echo "${PYTHON_IMAGE}" | sed 's/:/-/g' | sed 's/\./-/g' | sed 's/\//-/g')
export TEST_DOCKERFILE=Dockerfile-${TEST_IMAGE_VERSION}
export TEST_IMAGE=gcr.io/dnastack-container-store/client-library-testing:${TEST_IMAGE_VERSION}

echo "Base Image: ${PYTHON_IMAGE}"
echo "Test Tag: ${TEST_IMAGE_VERSION}"

cat Dockerfile-template | PYTHON_IMAGE=${PYTHON_IMAGE} envsubst > ${TEST_DOCKERFILE}

# Set --progress plain to see all build output.
docker buildx build --platform=linux/amd64,linux/arm64 --push \
  --progress auto \
  ${TEST_BUILD_OPTS} \
  -t ${TEST_IMAGE} \
  -f ${TEST_DOCKERFILE} .
docker run -it --rm \
  -v $(pwd)/.env:/app/.env:ro \
  --env-file .env \
  -e E2E_WEBDRIVER_TESTS_DISABLED=${WEBDRIVER_DISABLED} \
  ${TEST_IMAGE} ${TEST_CMD}