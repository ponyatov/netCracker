# \ var
# detect module/project name by current directory
MODULE  = $(notdir $(CURDIR))
# detect OS name (only Linux/MinGW)
OS      = $(shell uname -s)
# current date in the `ddmmyy` format
NOW     = $(shell date +%d%m%y)
# release hash: four hex digits (for snapshots)
REL     = $(shell git rev-parse --short=4 HEAD)
# current git branch
BRANCH  = $(shell git rev-parse --abbrev-ref HEAD)
# number of CPU cores (for parallel builds)
CORES   = $(shell grep processor /proc/cpuinfo| wc -l)
# Java project package
PACKAGE = com.nc.edu.ta.ponyatov.pr2
# / var

# \ dir
# current (project) directory
CWD     = $(CURDIR)
# compiled/executable files (target dir)
BIN     = $(CWD)/bin
# documentation & external manuals download
DOC     = $(CWD)/doc
# libraries / scripts
LIB     = $(CWD)/lib
# source code (not for all languages, Rust/C/Java included)
SRC     = $(CWD)/src
# temporary/flags/generated files
TMP     = $(CWD)/tmp
# project local CLASS_PATH
CP      = bin
# / dir

# \ jar
GJF_VER        = 1.7
GJF_JAR        = google-java-format-$(GJF_VER).jar
GJF            = lib/$(GJF_JAR)

JUNIT_VER      = 4.13.2
JUNIT_JAR      = junit-$(JUNIT_VER).jar
JUNIT          = lib/$(JUNIT_JAR)
CP            += $(JUNIT)

HAMCREST_VER   = 2.2
HAMCREST_JAR   = hamcrest-$(HAMCREST_VER).jar
HAMCREST       = lib/$(HAMCREST_JAR)
CP            += $(HAMCREST)
# / jar

# \ tool
# http/ftp download
CURL    = curl -L -o
PY      = python3
PIP     = pip3
PEP     = $(HOME)/.local/bin/autopep8
JAVA    = $(JAVA_HOME)/bin/java
JAVAC   = $(JAVA_HOME)/bin/javac
# / tool

# \ src
Y += metaL.py test_metaL.py
J += $(shell find src -type f -regex ".+.java$$")
# / src
S += $(Y)
S += $(J)

# \ cfg
CLASS   = $(shell echo $(J) | sed "s|\.java|.class|g" | sed "s|src/|bin/|g")
JPATH   = -cp $(shell echo $(CP) | sed "s/ /:/g")
JFLAGS  = -d $(BIN) $(JPATH)
# / cfg

# \ all
.PHONY: all
all: test format

# \ test
TESTS += $(PACKAGE).test.MyTest
TESTS += $(PACKAGE).test.PartialTest
TESTS += $(PACKAGE).test.FullTest

.PHONY: test
test: $(CLASS)
	$(JAVA) $(JPATH) \
		org.junit.runner.JUnitCore $(TESTS)
# / test

# \ format
.PHONY: format
format: tmp/format
tmp/format: $(J)
	$(JAVA) $(JPATH) -jar $(GJF) --replace $?
	touch $@
# / format

.PHONY: meta
meta: metaL.py
	$(PY) $<
	$(PEP) --ignore=E26,E302,E305,E401,E402,E701,E702 --in-place $<
# / all

# \ rule
$(CLASS): $(J)
	$(JAVAC) $(JFLAGS) $^
	$(MAKE) format
# / rule

# \ doc
.PHONY: doc
doc:
# / doc

# \ install
.PHONY: install update
install: $(OS)_install
	$(MAKE) gjf junit
	$(MAKE) update
update: $(OS)_update
	$(PIP) install --user -U autopep8

.PHONY: Linux_install Linux_update
Linux_install Linux_update:
ifneq (,$(shell which apt))
	sudo apt update
	sudo apt install -u `cat apt.txt apt.dev`
endif

gjf: $(GJF)
$(GJF):
	$(CURL) $@ https://github.com/google/google-java-format/releases/download/google-java-format-$(GJF_VER)/google-java-format-$(GJF_VER)-all-deps.jar

junit: $(JUNIT) $(HAMCREST)
$(JUNIT):
	$(CURL) $@ https://search.maven.org/remotecontent?filepath=junit/junit/$(JUNIT_VER)/$(JUNIT_JAR)

hamcrest: $(HAMCREST)
$(HAMCREST):
	$(CURL) $@ https://search.maven.org/remotecontent?filepath=org/hamcrest/hamcrest/$(HAMCREST_VER)/$(HAMCREST_JAR)
# / install

# \ merge
MERGE  = Makefile README.md apt.* .gitignore $(S)
MERGE += .vscode bin doc lib src tmp

.PHONY: dev
dev:
	git push -v
	git checkout $@
	git pull -v
	git checkout ponymuck -- $(MERGE)

.PHONY: ponymuck
ponymuck:
	git push -v
	git checkout $@
	git pull -v

.PHONY: release
release:
	git tag $(NOW)-$(REL)
	git push -v --tags
	$(MAKE) ponymuck

ZIP = $(TMP)/$(MODULE)_$(BRANCH)_$(NOW)_$(REL).src.zip

.PHONY: zip
zip:
	git archive --format zip --output $(ZIP) HEAD
	zip $(ZIP) lib/*.jar
# / merge
