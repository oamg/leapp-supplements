DIST_VERSION ?= 7
EXCESSIVE_UPTIME_LIMIT_DAYS ?= 30

PKGNAME := leapp-supplements
VERSION=$(shell grep -m1 "^Version:" packaging/$(PKGNAME).spec | grep -om1 "[0-9].[0-9.]*")
SPEC_FILE := $(PKGNAME).spec
TARBALL_PREFIX := $(PKGNAME)-$(VERSION)
TARBALL := $(TARBALL_PREFIX).tar.gz
ACTORS_TO_INSTALL := $(shell grep -v '^\#' actor-list.txt | tr '\n' ' ')

.PHONY: help clean tarball rpmbuild

help:
	@echo "Available targets:"
	@echo "  lint         : Run pylint and flake8"
	@echo "  pytest       : Run pytest"
	@echo "  test         : Run all tests (lint and pytest)"
	@echo "  shell-<env>" : Start and enter a container with the provided environment
	@echo "  rpmbuild     : Build RPM packages of the custom actors"
	@echo "  tarball      : Create a tarball of the source code from the current git HEAD"
	@echo "  clean        : Clean build artifacts and temporary files"
	@echo "  help         : Show this help message"
	@echo ""
	@echo "You may run containerized tests using strato-skipper (See the README)"
	@echo "Once skipper is installed, to run the tests in a containerized environment use the distribution specific targets"
	@echo "For example, to run all tests for RHEL8 run:"
	@echo "  make test-rhel8"
	@echo ""
	@echo "To build an RPM for RHEL7 upgrade, run:"
	@echo "  make rpmbuild DIST_VERSION=7"
	@echo "To build an RPM for RHEL8 upgrade, run:"
	@echo "  make rpmbuild DIST_VERSION=8"
	@echo ""
	@echo "Make sure to customize the actor-list.txt before building the RPM!"

rpmbuild: prepare
	rpmbuild -ba packaging/$(SPEC_FILE) \
		--define "_topdir $(shell pwd)/packaging" \
		--define "pkgname $(PKGNAME)" \
		--define "rhel $(DIST_VERSION)" \
		--define "nextrhel $$(($(DIST_VERSION) + 1))" \
		--define "dist .el$(DIST_VERSION)" \
		--define "actors_to_install $(ACTORS_TO_INSTALL)" \
		--define "excessive_uptime_limit_days $(EXCESSIVE_UPTIME_LIMIT_DAYS)"
	cp packaging/RPMS/*/*.rpm .
	cp packaging/SRPMS/*.rpm .

tarball:
	git archive --format=tar.gz --prefix=$(TARBALL_PREFIX)/ -o $(TARBALL) HEAD

prepare: check_actor_list clean tarball
# create the build directories
	mkdir -p packaging/{BUILD,RPMS,SOURCES,SRPMS,BUILDROOT}
	mv $(TARBALL) packaging/SOURCES/

# check if there are any actors in ACTORS_TO_INSTALL, exit if not
check_actor_list:
	@[ -n "$(ACTORS_TO_INSTALL)" ] || (echo "[ERR] actor-list.txt cannot be empty, no actors to install" && exit 1)

clean:
	rm -rf packaging/{BUILD,RPMS,SOURCES,SRPMS,BUILDROOT}
	rm -f *.rpm *tar.gz
	find . -name 'leapp.db' | grep "\.leapp/leapp.db" | xargs rm -f
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +

MAKER?=make
DISTROS := $(patsubst skipper-%,%,$(basename $(wildcard skipper-*.yaml)))
ACTIONS := shell test

# Parameters
# $1 == distribution
define shell_rules
shell-$1:
	@SKIPPER_CONF=${PWD}/skipper-$1.yaml skipper shell
endef

# Parameters
# $1 == distribution
# $2 == make target
define make_rules
$2-$1:
	@SKIPPER_CONF=${PWD}/skipper-$1.yaml skipper $(MAKER) $2

endef

MAKE_RULES := test lint pytest codespell

$(foreach d, $(DISTROS), \
	$(eval $(call shell_rules,$d)))

$(foreach d, $(DISTROS), \
	$(foreach m, $(MAKE_RULES), \
	$(eval $(call make_rules,$d,$m))))

test-all:
	for d in $(DISTROS); do $(MAKER) test-$$d; done


REPOS_PATH=repos
_SYSUPGSUP_REPOS="$(REPOS_PATH)/system_upgrade_supplements"
REPOSITORIES ?= $(shell ls $(_SYSUPGSUP_REPOS) | xargs echo | tr " " ",")
SYSUPGSUP_TEST_PATHS=$(shell echo $(REPOSITORIES) | sed -r "s|(,\\|^)| $(_SYSUPGSUP_REPOS)/|g")
TEST_PATHS:=$(SYSUPGSUP_TEST_PATHS)

LIBRARY_PATH=

# python version to run test with
_PYTHON_VENV=$${PYTHON_VENV:-python2.7}

REPORT_ARG=

ifeq ($(TEST_LIBS),y)
	LIBRARY_PATH=`python utils/library_path.py`
endif

ifdef REPORT
	REPORT_ARG=--junit-xml=$(REPORT)
endif

codespell:
	codespell --skip=./.git/*,*.pyc,leapp.db

lint:
	echo $()
	echo "--- Linting ... ---" && \
	SEARCH_PATH="$(TEST_PATHS)" && \
	echo "Using search path '$${SEARCH_PATH}'" && \
	echo "--- Running pylint ---" && \
	bash -c "[[ ! -z '$${SEARCH_PATH}' ]] && find $${SEARCH_PATH} -name '*.py' | sort -u | xargs pylint -j0" && \
	echo "--- Running flake8 ---" && \
	bash -c "[[ ! -z '$${SEARCH_PATH}' ]] && flake8 $${SEARCH_PATH}"

	if [[ "$(_PYTHON_VENV)" == "python2.7" ]] ; then \
		echo "--- Checking py3 compatibility ---" && \
		SEARCH_PATH=$(REPOS_PATH) && \
		bash -c "[[ ! -z '$${SEARCH_PATH}' ]] && find $${SEARCH_PATH} -name '*.py' | sort -u | xargs pylint --py3k" && \
		echo "--- Linting done. ---"; \
	fi

/tmp/leapp-repository:
	git clone --depth=1 https://github.com/oamg/leapp-repository.git /tmp/leapp-repository

conftest.py: /tmp/leapp-repository
	ln -sf /tmp/leapp-repository/conftest.py

pytest: /tmp/leapp-repository conftest.py
	snactor repo find --path /tmp/leapp-repository/repos/; \
	snactor repo find --path repos/; \
	$(_PYTHON_VENV) -m pytest --cov --cov-report=html $(REPORT_ARG) $(TEST_PATHS) $(LIBRARY_PATH)

test: codespell lint pytest
