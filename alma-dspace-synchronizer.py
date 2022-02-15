# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set syntax=python:
#########################
# (c) JR, 2022          #
#########################
from __future__ import annotations
import argparse
import dspace_api as ds_api
import dspace_solr as ds_solr

from configparser import ConfigParser, ExtendedInterpolation
from getopt import gnu_getopt
from sys import argv, stderr
import typing
if typing:
    import dspace_api, dspace_solr

my_parser = argparse.ArgumentParser(description="Synchronize DSpace ALAM ID to DSpace")

# Add arguments
my_parser.add_argument('-m', '--mode', metavar='mode', type=int, help="[1 - replace Aleph SYSNO | 2 - add missing ALMA ID]", required=True)
my_parser.add_argument('-c', '--config', metavar='config_path', type=str, help="path to config file")
my_parser.add_argument('-s', '--settings', metavar='settings', type=str, help="[iterative | complete]")

def do_start(dsapi: dspace_api, solr: dspace_solr, config):

    print("Testing app config: {}".format(config.get('MAPFILE','location')))

    print("Testing DSpace API: JSESSIONID = {}".format(dsapi.cookie))

    print("Pinging solr using the 'test' module of ds_solr: {}".format(solr.test.test_solr(ds_solr.solr)))
    
    print("Testing querying solr:")
    
    results = solr.solr.search('křečci')
    print("Saw {0} result(s).".format(len(results)))

    for result in results:
        print("HANDLE: {}".format(result['handle']))

    

if __name__ == '__main__':

    args = my_parser.parse_args()

    app_config = ConfigParser(interpolation=ExtendedInterpolation())

    if args.mode == 1:
        print("Mode is set to 1 - replace Aleph sysno")

    if args.config is None:
        print("No custom config file provided. Using default config.")
        app_config.read('./config.ini')
    else:
        print("Using custom config at {}".format(args.config))
        app_config.read(args.config)

    action = do_start

    action(ds_api, ds_solr, app_config)

    