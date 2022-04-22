# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set syntax=python:
#########################
# (c) JR, 2022          #
#########################
from __future__ import annotations
import argparse
from lib2to3.pgen2.token import LBRACE
import dspace_api as ds_api
import dspace_solr as ds_solr
import logging
import logging.config
import twisted.logger
import os

from twisted.internet import reactor
from twisted.internet import task
from twisted.python import log as twisted_log
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
my_parser.add_argument('-m', '--mode', metavar='mode', type=str, help="[1 - replace Aleph SYSNO | 2 - add missing ALMA ID]", required=True)
my_parser.add_argument('-c', '--config', metavar='config_path', type=str, help="path to config file")
my_parser.add_argument('-s', '--settings', metavar='settings', type=str, help="[iterative | complete]")
my_parser.add_argument('-l', "--limit", metavar='limit', type=int, help=['int - set maximum number of processed docs'], required=False)

def do_test(dsapi: dspace_api, solr: dspace_solr, config, args: argparse):

    try:
        if args.mode == 'replace':
            log.info("Mode is set to 1 - replace Aleph sysno")
        elif args.mode == 'add_missing':
            log.info("Mode is set to 2 - add missing ALMA ID")
        else:
            raise Exception("Invalid value of argument -m (mode): " + args.mode)
    except Exception as e:
        log.error(e, exc_info=True)
        raise e

    try:
        if args.config is None:

            log.debug("ARGS - config: {}".format(args.config))
            app_config_path = os.path.join(os.path.join(os.path.dirname(__file__)),'config','config.ini')
            
            log.debug("APP CONFIG PATH: {}".format(str(app_config_path)))
            log.info("No custom config file provided. Using default config.")
            
            log.debug("Config path: {}".format(app_config_path))
            
            app_config.read(app_config_path)
        else:
            log.info("Using custom config at {}".format(args.config))
            app_config.read(args.config)
    except Exception as e:
        log.error(e, exc_info=True)
        raise e

    # check if app config is valid
    try:
        log.info("Checking if app config is valid.")
        workflow_names = str(app_config.get('GENERAL','workflows')).split(sep=',')

        for name in workflow_names:
            if app_config.has_option('WF_CONFIGS', name) is False:
                raise KeyError("Key {} not in 'WF_CONFIGS section of the app_config".format(name))
        
        if app_config.has_option('WF_CONFIGS', args.mode) is False:
            raise ValueError("Mode (-m) '{}' not in 'WF_CONFIGS section of the app_config".format(args.mode))

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

def cbLoopDone(result):
    log.info(result)

def ebLoopFailed(failure):
    log.error(failure, exc_info=True)
    reactor.stop()
    raise e

def cbRunDone(result):
    log.info(result)
    reactor.stop()

def cbRunFailed(failure):
    log.error(failure, exc_info=True)
    reactor.stop()

def do_start(workflow_creator : workflow_creator, config : ConfigParser, should_loop=False, interval=None):

    # create looping task
    if should_loop is False:
        try:
            deferred = task.deferLater(reactor, 0, workflow_creator.run_workflow)
            deferred.addCallback(cbRunDone)
            deferred.addErrback(cbRunFailed)

        except Exception as e:
            raise e
    else:
        log.info("Interval: {}".format(interval))
        if interval == 'None':
            raise Exception("'should_loop' is set to {} - 'interval' cannot be {}".format(should_loop, interval))
        
        try:
            loop = task.LoopingCall(workflow_creator.run_workflow)
            loopDeferred = loop.start(float(interval))
            loopDeferred.addCallback(cbLoopDone)
            loopDeferred.addErrback(ebLoopFailed)
        except Exception as e:
            logging.exception(e)
            raise e

    reactor.run()
        

def parse_wf_config(wf_config_path):
    log.debug("parse_wf_config param value: {}".format(wf_config_path))
    log.debug("Current path: {}".format(str(os.path.dirname(os.path.abspath(__file__)))))
    
    wf_config_path = os.path.join(os.path.dirname(__file__), 'config', 'workflow', wf_config_path)
    
    log.debug("WF CONFIG PATH - FUCK: {}".format(str(wf_config_path)))
    # try to parse workflow config file
    # and store it for later use in workflow
    wf_config = ConfigParser(interpolation=ExtendedInterpolation())

    try:
        wf_config.read(wf_config_path)
    except Exception as e:
        logging.exception(e)
        raise e

    return wf_config

if __name__ == '__main__':

    # twisted log observer
    try:
        twisted.logger.STDLibLogObserver(__name__)
        # observer = twisted_log.PythonLoggingObserver('__name__')
    except Exception as e:
        logging.exception(e)
        raise e

    # create logger
    try:
        logging.config.fileConfig(fname=os.path.join(os.path.dirname(__file__),'config', 'logging.ini'), disable_existing_loggers=False)
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
        print("LOG", log)
        #log.debug("APP CONFIG BEFORE START {}".format(app_config))
        print("APP CONFIG BEFORE START {}".format(app_config))
        #log.debug("ARGS.MODE:", args.mode)
        print("ARGS.MODE:", args.mode)
        
        #log.debug("WF_WORKFLOWS IN CONFIG.INI: {}".format(app_config.get("WF_CONFIGS", args.mode)))
        print("WF_WORKFLOWS IN CONFIG.INI: {}".format(app_config.get("WF_CONFIGS", args.mode)))

        wf_config = parse_wf_config(app_config.get('WF_CONFIGS', args.mode))
        
        loop = wf_config.getboolean('GENERAL','loop')
        interval = wf_config.get('GENERAL','interval')
        
        if args.mode == 'replace':  
            action(ReplaceWorkflowCreator(ds_api, ds_solr, wf_config, args), app_config, loop, interval)
        elif args.mode == 'add_missing':
            action(AddMissingWorkflowCreator(ds_api, ds_solr, wf_config, args), app_config, loop, interval)
        else:
            log.error("Invalid value of argument -m (mode):" + args.mode, exc_info=True)
            raise Exception ("Invalid value of argument -m (mode): " + args.mode)

    except Exception as e:
        log.error(e, exc_info=True)
        raise e

    exit(0)



    