#!/bin/python

FULL_PATH = open('path_file.txt', 'r').read().replace("\n", '')

from sys import path
path.insert(0, FULL_PATH)

from SubModuleSystem import SUMOS

S = SUMOS('%s/test_dir' % FULL_PATH)

S.Check()

S.List()

#print(S.SMSplugins)

S.Call('test.cfg')
