.PHONY: clean test

clean:
	rm -rf build dist *.egg-info
	rm -rf *profile.svg *.pstats

test:
	PYTHONPATH=. nosetests -w test/ -v

publish:
	python setup.py sdist bdist_wheel upload
