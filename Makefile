exe_name=popsinstaller
python-ver=3.8

build:
	cython -3 popsinstaller.py --embed
	gcc -o $(exe_name) popsinstaller.c -lpython$(python-ver) -I/usr/include/python$(python-ver)

clean:
	rm -f $(exe_name) popsinstaller.c
