all:

test:
	pytest pyfermions

run-notebooks:
	jupyter nbconvert --execute --inplace notebooks/error_bounds.ipynb
	jupyter nbconvert --execute --inplace notebooks/evenbly_white.ipynb
	jupyter nbconvert --execute --inplace notebooks/figures.ipynb
	jupyter nbconvert --execute --inplace notebooks/mera1d.ipynb
	jupyter nbconvert --execute --inplace notebooks/mera2d.ipynb
	jupyter nbconvert --execute --inplace notebooks/selesnick.ipynb

export-notebooks:
	cd notebooks && jupyter nbconvert --to pdf *.ipynb

pretty:
	black --py36 pyfermions setup.py

upload-release:
	python -c "import wheel"  # check upload dependencies
	python -c "import subprocess; assert b'dev' not in subprocess.check_output('python setup.py --version', shell=True).strip(), 'trying to upload dev release'"
	python setup.py sdist bdist_wheel
	twine upload dist/* --sign
