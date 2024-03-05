# Run the tests in isolation.

set -e

export PYTHON_IMAGE=${1}
export TEST_IMAGE_PLATFORM=${2:-linux/amd64}
export TEST_IMAGE_VERSION=$(echo "${PYTHON_IMAGE}" | sed 's/:/-/g' | sed 's/\./-/g' | sed 's/\//-/g')
export TEST_IMAGE=gcr.io/dnastack-container-store/client-library-testing:${TEST_IMAGE_VERSION}

docker run -it --rm \
  -v $(pwd)/.env:/app/.env:ro \
  --platform ${TEST_IMAGE_PLATFORM} \
  --env-file .env \
  ${TEST_IMAGE}