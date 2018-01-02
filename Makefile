test:
	pytest -v

ship:
	python setup.py sdist bdist_wheel
	twine upload dist/* --skip-existing

dev:
	gulp --cwd geography/staticapp/

database:
	dropdb geography --if-exists
	createdb geography
