.PHONY: test ship

test:
	flake8 cpi
	coverage run test.py
	coverage report -m


ship:
	rm -rf build/
	python setup.py sdist bdist_wheel
	twine upload dist/* --skip-existing
