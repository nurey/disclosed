#!/usr/bin/env python2.5
# encoding: utf-8
"""
app_yaml.py - app.yaml postprocessor to add version based on svnversion

Created by Ilia Lobsanov on 2008-06-16.
Copyright (c) 2008 Nurey Networks Inc. All rights reserved.

"""

import sys
import os
import yaml


def main():
  #svnversion 
  print "# DO NOT MODIFY THIS FILE. USE app.yaml.in"
  svnversion = os.popen("svnversion -nc .. | sed -e 's/^[^:]*://;s/[A-Za-z]//'").readline().rstrip("\n");
  app = yaml.load(sys.stdin)
  app["version"] = int(svnversion)
  print yaml.dump(app, indent=2)

if __name__ == '__main__':
	main()

