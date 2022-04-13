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
import logging
import logging.config

from workflow_creator.replace_wf_creator import ReplaceWorkflowCreator
from workflow_creator.add_missing_wf_creator import AddMissingWorkflowCreator
from configparser import ConfigParser, ExtendedInterpolation
from getopt import gnu_getopt
from sys import argv, stderr
import typing
if typing:
    import dspace_api, dspace_solr, workflow_creator

my_parser = argparse.ArgumentParser(description="Synchronize DSpace ALAM ID to DSpace")

# Add arguments
my_parser.add_argument('-m', '--mode', metavar='mode', type=int, help="[1 - replace Aleph SYSNO | 2 - add missing ALMA ID]", required=True)
my_parser.add_argument('-c', '--config', metavar='config_path', type=str, help="path to config file")
my_parser.add_argument('-s', '--settings', metavar='settings', type=str, help="[iterative | complete]")
my_parser.add_argument('-l', "--limit", metavar='limit', type=int, help=['int - set maximum number of processed docs'])

def do_test(dsapi: dspace_api, solr: dspace_solr, config, args: argparse):

    try:
        if args.mode == 1:
            log.info("Mode is set to 1 - replace Aleph sysno")
        elif args.mode == 2:
            log.info("Mode is set to 2 - add missing ALMA ID")
        else:
            raise Exception("Invalid value of argument -m (mode): " + args.mode)
    except Exception as e:
        log.error(e, exc_info=True)
        raise e

    try:
        if args.config is None:
            log.info("No custom config file provided. Using default config.")
            app_config.read('./config.ini')
        else:
            log.info("Using custom config at {}".format(args.config))
            app_config.read(args.config)
    except Exception as e:
        log.error(e, exc_info=True)
        raise e

    try:
        if args.limit is None:
            log.info("No limit for max processed docs is set. All relevant docs found will be processed.")
        else:
            log.info("Limit of max processed docs set to {0}. Only first {0} relevant docs found will be processed.".format(
                args.limit))
    except Exception as e:
        log.error(e, exc_info=True)
        raise e

    try:
        log.debug("Testing app config: {}".format(config.get('MAPFILE','location')))
    except Exception as e:
        log.error(e, exc_info=True)
        raise e
    
    try:
        log.debug("Testing DSpace API: JSESSIONID = {}".format(dsapi.cookie))
    except Exception as e:
        log.error(e, exc_info=True)
        raise e

    try:
        log.debug("Pinging solr using the 'test' module of ds_solr: {}".format(solr.test.test_solr(ds_solr.solr)))
        log.debug("Testing querying solr:")
        
        results = solr.solr.search('křečci')
        log.debug("Saw {0} result(s).".format(len(results)))

        for result in results:
            log.debug("HANDLE: {}".format(result['handle']))
    
    except Exception as e:
        log.error(e, exc_info=True)
        raise e
    

def do_start(workflow_creator : workflow_creator):

    print(workflow_creator.run_workflow())

    

if __name__ == '__main__':

    # create logger
    try:
        logging.config.fileConfig(fname='logging.ini', disable_existing_loggers=False)
        log = logging.getLogger(__name__)
        
    except Exception as e:
        logging.exception(e)
        raise e

    # create handlers

    args = my_parser.parse_args()

    app_config = ConfigParser(interpolation=ExtendedInterpolation())

    

    try:
        do_test(ds_api, ds_solr, app_config, args)
    except Exception as e:
        log.error(e, exc_info=True)
        raise e

    try:
        action = do_start

        if args.mode == 1:
            action(ReplaceWorkflowCreator(ds_api, ds_solr, app_config, args))
        elif args.mode == 2:
            action(AddMissingWorkflowCreator(ds_api, ds_solr, app_config, args))
        else:
            log.error("Invalid value of argument -m (mode):" + args.mode, exc_info=True)
            raise Exception ("Invalid value of argument -m (mode): " + args.mode)

    except Exception as e:
        log.error(e, exc_info=True)
        raise e

    exit(0)



    