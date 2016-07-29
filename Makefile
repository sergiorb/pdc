init:
	
	virtualenv -p python3 pdc_env
	./pdc_env/bin/pip3 install -r requirements.txt

test:

	./pdc_env/bin/python3 -m unittest tests/tests.py -v