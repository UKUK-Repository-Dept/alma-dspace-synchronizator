from . import Workflow

class ReplaceWorkflow(Workflow):

    def find_input_file(self):
        print(self.config.get("MAPFILE","location"))
        return "ReplaceWorkflow - find_input_file - DONE"

    def find_valid_docs_in_solr(self):
        return "ReplaceWorkflow - find_valid_docs_in_solr - DONE"

    
    def find_valid_docs_in_mapfile(self):
        return "ReplaceWorkflow - find_valid_docs_in_mapfile - DONE"
    

    def compare_solr_to_mapfile(self):
        return "ReplaceWorkflow - compare_solr_to_mapfile - DONE"

    
    def update_dspace_records(self):
        return "ReplaceWorkflow - update_dspace_records - DONE"