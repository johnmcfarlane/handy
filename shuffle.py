#!/usr/bin/python3

from glob import glob
from random import shuffle
from subprocess import call
from sys import argv

def main(files):
	print ('\n'.join([file for file in files]))
	shuffle(files)
	for file in files:
		print (call(['omxplayer', file]))

if __name__ == '__main__':
	if len(argv) == 1:
		print ('Wildcard?')
	else:
		main(argv[1:])
