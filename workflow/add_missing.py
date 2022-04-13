from . import Workflow

class AddMissingWorkflow(Workflow):

    def find_input_file(self):
        return "AddMissingWorkflow - find_input_file - DONE"

    def find_valid_docs_in_solr(self):
        return "AddMissingWorkflow - find_valid_docs_in_solr - DONE"

    def compare_solr_to_mapfile(self):
        return "AddMissingWorkflow - compare_solr_to_mapfile - DONE"

    def prepare_record_updates(self):
        return "AddMissingWorkflow - prepare_record_updates - DONE"

    
    def update_dspace_records(self):
        return "AddMissingWorkflow - update_dspace_records - DONE"