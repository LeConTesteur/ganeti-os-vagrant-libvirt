VERSION:=0.1
REVISION=1
DEB_NAME=ganeti-os-vagrant-libvirt_$(VERSION)-$(REVISION)_amd64
DEST=dist/$(DEB_NAME)
DEST_DEB_PATH=$(DEST).deb

.PHONY: dist

test: $(wildcard test/*)
	python3 -m unittest discover -s test


$(DEST)/var/lib/ganeti: $(wildcard src/*)
	mkdir -p $@
	cp $^ $@

$(DEST)/DEBIAN: control
	mkdir -p $@
	cp $^ $@

$(DEST_DEB_PATH): $(DEST)/var/lib/ganeti $(DEST)/DEBIAN
	dpkg-deb --build --root-owner-group $(DEST)

dist: $(DEST_DEB_PATH)