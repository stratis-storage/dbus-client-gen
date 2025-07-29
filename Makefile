ifeq ($(origin MONKEYTYPE), undefined)
  PYTHON = python3
else
  PYTHON = MONKEYTYPE_TRACE_MODULES=dbus_client_gen monkeytype run
endif

MONKEYTYPE_MODULES = dbus_client_gen._managed_objects

.PHONY: lint
lint:
	pylint setup.py
	pylint src/dbus_client_gen --disable=duplicate-code
	pylint tests

.PHONY: test
test:
	${PYTHON} -m unittest discover --verbose tests

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

PYREVERSE_OPTS = --output=pdf
.PHONY: view
view:
	-rm -Rf _pyreverse
	mkdir _pyreverse
	PYTHONPATH=src pyreverse ${PYREVERSE_OPTS} --project="dbus-client-gen" src/dbus_client_gen
	mv classes_dbus-client-gen.pdf _pyreverse
	mv packages_dbus-client-gen.pdf _pyreverse

.PHONY: yamllint
yamllint:
	yamllint --strict .github/workflows/main.yml

.PHONY: package
package:
	(umask 0022; python -m build; python -m twine check --strict ./dist/*)

.PHONY: legacy-package
legacy-package:
	python3 setup.py build
	python3 setup.py install

.PHONY: apply
apply:
	@echo "Modules traced:"
	@monkeytype list-modules
	@echo
	@echo "Annotating:"
	@for module in ${MONKEYTYPE_MODULES}; do \
	  monkeytype --verbose apply  --sample-count --ignore-existing-annotations $${module} > /dev/null; \
	done
