#!/bin/sh

python3 ./test/clean.py
python3 ./cli.py < ./test/test.in > ./test/test.out
python3 ./test/clean.py
pytest -s test/pytest_cloudshop.py
