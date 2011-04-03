#!/usr/bin/env python

""" Test Expressions """

import test_utils

TEST_FILE = "expressions.py"

test_descriptions = open("%s/%s"%(test_utils.RELATIVE_TEST_PATH,
  TEST_FILE)).readlines()

ConvertTree = test_utils.ConvertTree

def TestExpressions():
  t = test_utils.SetUp(TEST_FILE)
  for i in range(len(t.body)):
    description = test_descriptions[i]
    ConvertTree.description = "Test `%s`"%(description.strip())
    yield ConvertTree, t.body[i]
