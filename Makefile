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
	yapf -ir pyfermions
