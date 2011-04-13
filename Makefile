# Unit-testing, docs.

VIRTUALENV?=virtualenv

all: test flakes pep8

env:
	mkdir -p .download_cache
	rm -rf env/
	$(VIRTUALENV) --clear --no-site-packages env
	env/bin/pip install --download-cache=.download_cache pyparsing sphinx pyflakes pep8
	echo ">> Run 'source env/bin/activate'" 

test:
	env/bin/python -m unittest discover -v

doc:
	cd doc && make html

flakes:
	-env/bin/pyflakes loggerglue

pep8:
	# E501 line too long
	-env/bin/pep8 --repeat --statistics --ignore=E501 loggerglue

.PHONY: env doc
