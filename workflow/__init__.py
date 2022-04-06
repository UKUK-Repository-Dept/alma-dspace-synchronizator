from abc import ABC, abstractmethod
import typing
if typing:
    import dspace_api, dspace_solr, configparser

class Workflow(ABC):
    """
    Operations permissible in the worfow
    """

    def __init__(self, dsapi: dspace_api, solr: dspace_solr, config: configparser.ConfigParser) -> None:
        self.__dsapi = dsapi
        self.__dspace_solr = solr
        self.__config = config

    @property
    def config(self) -> configparser.ConfigParser:
        return self.__config

    @property
    def dsapi(self) -> dspace_api:
        return self.__dsapi

    @property
    def solr(self) -> dspace_solr:
        return self.__dspace_solr

    @abstractmethod
    def find_input_file(self):
        pass

    @abstractmethod
    def find_valid_docs_in_solr(self):
        pass

    @abstractmethod
    def find_valid_docs_in_mapfile(self):
        pass
    
    @abstractmethod
    def compare_solr_to_mapfile(self):
        pass

    @abstractmethod
    def update_dspace_records(self):
        pass

    