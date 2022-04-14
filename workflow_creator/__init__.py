from abc import ABC, abstractmethod
from time import sleep
import typing
import logging
if typing:
    import dspace_api as ds_api
    import dspace_solr as ds_solr
    import argparse
    from workflow import Workflow
    from configparser import ConfigParser, ExtendedInterpolation


class WorkflowCreator(ABC):

    """
    The Creator class declares the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """

    def __init__(self, ds_api: ds_api, ds_solr: ds_solr, config: ConfigParser, args : argparse) -> None:
        self.__ds_api = ds_api
        self.__ds_solr = ds_solr
        self.__config = config
        self.__args = args
        self.__log = logging.getLogger(__name__)

    @abstractmethod
    def factory_method(self, ds_api, ds_solr, config, args) -> Workflow:
        """
        Note that the Creator may also provide some default implementation of
        the factory method.
        """
        pass

    def run_workflow(self) -> str:
        """
        Also note that, despite its name, the Creator's primary responsibility
        is not creating products. Usually, it contains some core business logic
        that relies on Product objects, returned by the factory method.
        Subclasses can indirectly change that business logic by overriding the
        factory method and returning a different type of product from it.
        """

        # Call the factory method to create a Workflow object.
        workflow = self.factory_method(self.__ds_api, self.__ds_solr, self.__config, self.__args)

        # Now, use the workflow.
        try:
            result = workflow.find_input_file()
            self.__log.info(result)
        except Exception as e:
            self.__log.error(e, exc_info=True)
            raise e

        try:
            result = workflow.gather_valid_docs_in_solr()
            self.__log.info(result)
        except Exception as e:
            self.__log.error(e, exc_info=True)
            raise e

        try:
            result = self.process_docs(workflow)
            self.__log.info(result)
        except Exception as e:
            self.__log.error(e, exc_info=True)
            raise e

        return "Finished {} workflow.".format(workflow.__class__.__name__)


    def process_docs(self, workflow: Workflow):

        found = 0 
        
        for doc in workflow.gathered_docs:

            self.__log.info("Found {}".format(found))

            if found == workflow.args.limit:
                self.__log.info("Reached the limit of gathered docs. Ending processing.")
                
                break

            found += 1
            
            try:
                result = workflow.preprocess_solr_docs(doc)
                self.__log.info(result)
            except Exception as e:
                workflow.log.error(e)
                self.__log.error(e, exc_info=True)
                continue

            try:
                result = workflow.compare_solr_to_mapfile(doc)
                self.__log.info(result)
            except Exception as e:
                workflow.log.error(e)
                self.__log.error(e, exc_info=True)
                continue

            try:
                result = workflow.prepare_record_updates(doc)
                self.__log.info(result)
            except Exception as e:
                workflow.log.error(e)
                self.__log.error(e, exc_info=True)
                continue

            try:
                result = workflow.update_dspace_records(doc)
                self.__log.info(result)
            except Exception as e:
                workflow.log.error(e)
                self.__log.error(e, exc_info=True)
                continue

            sleep(1)

        message = "Processed {} docs in {}".format(str(found), str(workflow.__class__.__name__))
        
        return message