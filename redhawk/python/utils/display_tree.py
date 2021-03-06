#!/usr/bin/env python

from __future__ import absolute_import
import redhawk.utils.get_ast as G

import ast
import pprint
import sys

filename = sys.argv[1]

pprint.pprint(ast.dump(
  G.GetLanguageSpecificTree(filename, 
                            database = None, 
                            language='python')))
