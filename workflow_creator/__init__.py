from abc import ABC, abstractmethod

class WorkflowCreator(ABC):

    """
    The Creator class declares the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """

    def __init__(self, ds_api, ds_solr, config) -> None:
        self.__ds_api = ds_api
        self.__ds_solr = ds_solr
        self.__config = config

    @abstractmethod
    def factory_method(self, ds_api, ds_solr, config):
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
        workflow = self.factory_method(self.__ds_api, self.__ds_solr, self.__config)

        # Now, use the workflow.
        try:
            result = workflow.find_input_file()
            print(result)
        except Exception as e:
            raise e

        try:
            result = workflow.find_valid_docs_in_solr()
            print(result)
        except Exception as e:
            raise e

        try:
            result = workflow.find_valid_docs_in_mapfile()
            print(result)
        except Exception as e:
            raise e

        try:
            result = workflow.compare_solr_to_mapfile()
            print(result)
        except Exception as e:
            raise e

        try:
            result = workflow.update_dspace_records()
            print(result)
        except Exception as e:
            raise e

        # result = f"Creator: The same creator's code has just worked with {workflow.run()}"

        return result