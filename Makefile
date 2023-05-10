DIST_VERSION ?= 7

PKGNAME := leapp-supplements
VERSION=$(shell grep -m1 "^Version:" packaging/$(PKGNAME).spec | grep -om1 "[0-9].[0-9.]*")
SPEC_FILE := $(PKGNAME).spec
TARBALL_PREFIX := $(PKGNAME)-$(VERSION)
TARBALL := $(TARBALL_PREFIX).tar.gz
ACTORS_TO_INSTALL := $(shell grep -v '^\#' actor-list.txt | tr '\n' ' ')

.PHONY: help clean tarball rpmbuild

help:
	@echo "Available targets:"
	@echo "  rpmbuild   : Build RPM packages of the custom actors"
	@echo "  tarball    : Create a tarball of the source code from the current git HEAD"
	@echo "  clean      : Clean build artifacts and temporary files"
	@echo "  help       : Show this help message"
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
		--define "actors_to_install $(ACTORS_TO_INSTALL)"
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
