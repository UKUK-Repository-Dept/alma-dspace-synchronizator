from . import WorkflowCreator
from workflow import Workflow
from workflow.add_missing import AddMissingWorkflow

class AddMissingWorkflowCreator(WorkflowCreator):


    """
    Note that the signature of the method still uses the abstract product type,
    even though the concrete product is actually returned from the method. This
    way the Creator can stay independent of concrete product classes.
    """

    def factory_method(self, ds_api, ds_solr, config) -> Workflow:
        return AddMissingWorkflow(ds_api, ds_solr, config)