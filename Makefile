TOX=tox

.PHONY: lint
lint:
	pylint setup.py
	pylint src/dbus_client_gen --disable=duplicate-code
	pylint tests

.PHONY: coverage
coverage:
	coverage --version
	coverage run --timid --branch -m unittest discover tests
	coverage report -m --fail-under=100 --show-missing --include="./src/*"

.PHONY: fmt
fmt:
	isort setup.py src tests
	black .

.PHONY: fmt-travis
fmt-travis:
	isort --diff --check-only setup.py src tests
	black . --check

.PHONY: test
test:
	$(TOX) -c tox.ini -e test

PYREVERSE_OPTS = --output=pdf
.PHONY: view
view:
	-rm -Rf _pyreverse
	mkdir _pyreverse
	PYTHONPATH=src pyreverse ${PYREVERSE_OPTS} --project="dbus-client-gen" src/dbus_client_gen
	mv classes_dbus-client-gen.pdf _pyreverse
	mv packages_dbus-client-gen.pdf _pyreverse

.PHONY: upload-release
upload-release:
	python setup.py register sdist upload

.PHONY: yamllint
yamllint:
	yamllint --strict .github/workflows/main.yml
