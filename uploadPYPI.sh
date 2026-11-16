#!/bin/sh
# Build and upload cuPAMI.
#   sh uploadPYPI.sh          upload to TestPyPI (default)
#   sh uploadPYPI.sh pypi     upload to PyPI
set -eu
cd "$(dirname "$0")"

case "${1:-testpypi}" in
    testpypi) repository=testpypi; page=https://test.pypi.org/project/cupami/ ;;
    pypi)     repository=pypi;     page=https://pypi.org/project/cupami/ ;;
    *) echo "usage: sh uploadPYPI.sh [testpypi|pypi]" >&2; exit 2 ;;
esac

# Build into a fresh directory so older releases are never uploaded.
release_dir=$(mktemp -d)
trap 'python3 -c "import shutil, sys; shutil.rmtree(sys.argv[1])" "$release_dir"' EXIT

echo "Running setup"
python3 setup.py sdist --dist-dir "$release_dir" bdist_wheel --dist-dir "$release_dir"
python3 -m twine check "$release_dir"/*

echo "Uploading cuPAMI to $repository"
python3 -m twine upload --repository "$repository" "$release_dir"/*
echo "Completed: $page"
