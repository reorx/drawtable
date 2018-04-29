.PHONY: clean test

clean:
	rm -rf build dist *.egg-info
	rm -rf *profile.svg *.pstats

test:
	pytest -vv

publish:
	python setup.py sdist bdist_wheel upload
