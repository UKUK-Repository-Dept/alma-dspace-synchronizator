from abc import ABC, abstractmethod
from time import sleep
import typing
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
            print(result)
        except Exception as e:
            raise e

        try:
            result = workflow.gather_valid_docs_in_solr()
            print(result)
        except Exception as e:
            raise e

        try:
            result = self.process_docs(workflow)
            print(result)
        except Exception as e:
            raise e

        return "Finished {} workflow.".format(workflow.__class__.__name__)


    def process_docs(self, workflow: Workflow):

        found = 0 

        for doc in workflow.gathered_docs:
            found += 1
            
            try:
                result = workflow.preprocess_solr_docs(doc)
                print(result)
            except Exception as e:
                print("{} - Doc {}: Error in processing.".format(workflow.__class__.__name__,doc['handle']))
                raise e

            try:
                result = workflow.compare_solr_to_mapfile(doc)
                print(result)
            except Exception as e:
                print("{} - Doc {}: Error in processing.".format(workflow.__class__.__name__,doc['handle']))
                raise e

            try:
                result = workflow.prepare_record_updates(doc)
                print(result)
            except Exception as e:
                print("{} - Doc {}: Error in processing.".format(workflow.__class__.__name__,doc['handle']))
                raise e

            try:
                result = workflow.update_dspace_records(doc)
                print(result)
            except Exception as e:
                print("{} - Doc {}: Error in processing.".format(workflow.__class__.__name__,doc['handle']))
                raise e

            if found == workflow.args.limit:
                print("Reached the limit of gathered docs. Ending processing.")
                
                break
            
            sleep(1)
        
        return "Processed " + str(found) + " docs in " + str(workflow.__class__.__name__)