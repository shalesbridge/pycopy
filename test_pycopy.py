#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import unittest

import tempdir

import pycopy

__version__ = '0.1'

TEST_FILES = {
    'Moby Dick.txt': 'Herman Melville',
    'Great Expectations.txt': 'Charles Dickens',
}

class Test_01(unittest.TestCase):
    def test_01(self):
        with tempdir.in_tempdir() as td:
            os.mkdir('src')
            os.mkdir('dst')
            with open(os.path.join('src', 'Moby Dick.txt'), 'wb') as w:
                w.write(TEST_FILES['Moby Dick.txt'])
            with open(os.path.join('src', 'Great Expectations.txt'), 'wb') as w:
                w.write(TEST_FILES['Great Expectations.txt'])
            pycopy.pycopy('src', 'dst')
            self.assertTrue(os.path.exists(os.path.join('dst',
                'Moby Dick.txt'
                )))
            self.assertTrue(os.path.exists(os.path.join('dst',
                'Great Expectations.txt')))



            


if __name__ == '__main__':
    unittest.main()
