set -e

# This script is to run the e2e test INSIDE the container.
#
# What this scripts will not do:
# - Start a docker container to run the test.

TEST_SANDBOX_DIR=/tmp/test-sandbox

# Copy to a separate
rm -rf ${TEST_SANDBOX_DIR} || echo 'Not exists'
mkdir -p ${TEST_SANDBOX_DIR}
cp -r \
  dist/*.whl \
  scripts \
  tests \
  ${TEST_SANDBOX_DIR}
cd ${TEST_SANDBOX_DIR}

# Install the package
pip install *.whl

# Install additional requirements
./scripts/setup-e2e-tests-for-linux.sh

# Run the test
./scripts/run-e2e-tests.sh $@