VERSION:=0.1
REVISION=1
DEB_NAME=ganeti-os-vagrant-libvirt_$(VERSION)-$(REVISION)_amd64
DEST=dist/$(DEB_NAME)
DEST_DEB_PATH=$(DEST).deb

.PHONY: dist

test: $(wildcard tests/*)
	python3 -m unittest discover -s tests


$(DEST)/usr/share/ganeti/ganeti-os-vagrant-libvirt: $(wildcard src/*)
	mkdir -p $@
	cp $^ $@

$(DEST)/DEBIAN: control
	mkdir -p $@
	cp $^ $@

$(DEST_DEB_PATH): $(DEST)/usr/share/ganeti/ganeti-os-vagrant-libvirt $(DEST)/DEBIAN
	dpkg-deb --build --root-owner-group $(DEST)

dist: $(DEST_DEB_PATH)