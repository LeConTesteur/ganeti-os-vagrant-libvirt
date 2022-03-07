VERSION:=0.0.1
DEB_NAME=ganeti-os-vagrant-libvirt_$(VERSION)_amd64
DEST=dist/$(DEB_NAME)
DEST_DEB_PATH=$(DEST).deb

.PHONY: dist

test: $(wildcard tests/*)
	tox test


$(DEST)/usr/share/ganeti/ganeti-os-vagrant-libvirt: $(wildcard src/*)
	mkdir -p $@
	cp $^ $@

$(DEST)/DEBIAN: control
	mkdir -p $@
	cp $^ $@

$(DEST_DEB_PATH): $(DEST)/usr/share/ganeti/ganeti-os-vagrant-libvirt $(DEST)/DEBIAN
	dpkg-deb --build --root-owner-group $(DEST)

dist: $(DEST_DEB_PATH)

pybuild:
	tox build