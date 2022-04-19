# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set syntax=python:
#########################
# (c) JR, 2022          #
#########################
from abc import ABC, abstractmethod
import typing
import logging
if typing:
    import dspace_api, dspace_solr, configparser, argparse

class Workflow(ABC):
    """
    Operations permissible in the worfow
    """

    def __init__(self, dsapi: dspace_api, solr: dspace_solr, config: configparser.ConfigParser, args: argparse) -> None:
        self.__dsapi = dsapi
        self.__dspace_solr = solr
        self.__config = config
        self.__args = args
        self.__gathered_docs = list()
        self.__mapfile_csv_list = list()
        self.__mapfile_csv_fieldnames = list()
        self.__log = logging.getLogger(__name__)

    @property
    def args(self) -> argparse:
        return self.__args

    @property
    def config(self) -> configparser.ConfigParser:
        return self.__config

    @property
    def dsapi(self) -> dspace_api:
        return self.__dsapi

    @property
    def solr(self) -> dspace_solr:
        return self.__dspace_solr.solr

    @property
    def gathered_docs(self) -> list:
        return self.__gathered_docs

    @gathered_docs.setter
    def gathered_docs(self, value):
        self.__gathered_docs = value

    @property
    def mapfile_csv_list(self) -> list:
        return self.__mapfile_csv_list

    @mapfile_csv_list.setter
    def mapfile_csv_list(self, value):
        self.__mapfile_csv_list = value

    @property
    def mapfile_csv_fieldnames(self):
        return self.__mapfile_csv_fieldnames

    @mapfile_csv_fieldnames.setter
    def mapfile_csv_fieldnames(self, value):
        self.__mapfile_csv_fieldnames = value

    @property
    def log(self):
        return self.__log

    @abstractmethod
    def find_input_file(self):
        pass

    @abstractmethod
    def gather_valid_docs_in_solr(self):
        pass

    @abstractmethod
    def preprocess_solr_docs(self):
        pass
    
    @abstractmethod
    def compare_solr_to_mapfile(self):
        pass

    @abstractmethod
    def prepare_record_updates(self):
        pass

    @abstractmethod
    def update_dspace_records(self):
        pass

    