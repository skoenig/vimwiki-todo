SHELL = /bin/sh

INSTALL = /usr/bin/install
INSTALL_PROGRAM = $(INSTALL)

# The directory to install the scripts in.
ifdef TODO_DIR
	tododir = $(TODO_DIR)
else
	tododir = ~/vimwiki
endif

bindir = ~/bin

installdirs:
	@if [ ! -d $(tododir) ]; then \
		echo "directory $(tododir) does not exist, set TODO_DIR to correct location"; \
		exit 1; \
	fi
	@if [ ! -d $(bindir) ]; then mkdir $(bindir); fi

install: installdirs
	$(INSTALL_PROGRAM) todo $(DESTDIR)$(tododir)/todo && \
		ln -sf $(DESTDIR)$(tododir)/todo $(DESTDIR)$(bindir)/todo
	@echo "todo" >> $(DESTDIR)$(tododir)/.gitignore

uninstall:
	rm -f $(DESTDIR)$(tododir)/todo $(DESTDIR)$(bindir)/todo

install-recur: installdirs
	$(INSTALL_PROGRAM) recur.py $(DESTDIR)$(tododir)/recur.py && \
		sudo ln -sf $(DESTDIR)$(tododir)/recur.py /etc/cron.daily/add_recurring_todos
	@echo "recur.py" >> $(DESTDIR)$(tododir)/.gitignore

uninstall-recur:
	sudo rm -f $(DESTDIR)$(tododir)/recur.py /etc/cron.daily/add_recurring_todos

.PHONY: test
test:
	python -m pip install -e .[tests]
	python -m pytest
