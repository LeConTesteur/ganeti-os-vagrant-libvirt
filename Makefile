VERSION:=0.0.7
DEB_NAME=ganeti-os-vagrant-libvirt_$(VERSION)_amd64
DEST=dist/$(DEB_NAME)
DEST_DEB_PATH=$(DEST).deb
SRC_FILES := $(wildcard src/*)
SRC_FILES := $(filter-out src/__pycache__ src/ganeti_os_vagrant_libvirt.egg-info,$(SRC_FILES))

.PHONY: dist test

test: $(wildcard tests/*)
	tox test

$(DEST)/usr/share/ganeti/os/ganeti-os-vagrant-libvirt: $(SRC_FILES)
	mkdir -p $@
	cp $^ $@

$(DEST)/DEBIAN: control
	mkdir -p $@
	cp $^ $@

$(DEST_DEB_PATH): $(DEST)/usr/share/ganeti/os/ganeti-os-vagrant-libvirt $(DEST)/DEBIAN
	dpkg-deb --build --root-owner-group $(DEST)

dist: $(DEST_DEB_PATH)

pybuild:
	tox build
