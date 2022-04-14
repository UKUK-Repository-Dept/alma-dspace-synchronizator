from requests import request
from . import Workflow
from utility import FileUtils, SolrUtils, MapfileUtils, ReportingUtils

class ReplaceWorkflow(Workflow):

    def find_input_file(self):

        self.log.info("Trying to find and parse mapfile.")
        
        # Get mapfile path from config, if none, raise an Exception
        try:
            if self.config.get("MAPFILE", "location") is None:
                raise Exception("Mapfile_path is " + self.config.get("MAPFILE", "location"))
        except Exception as e:
            self.log.error(e, exc_info=True)
            raise e

        # check if file realy exists in this path
        # presume that path is local (at least for now)
        try:
            if FileUtils.file_exists(self.config.get("MAPFILE", "location")) is False:
                raise IOError(self.config.get("MAPFILE", "location") + " not found")
        except Exception as e:
            self.log.error(e, exc_info=True)
            raise e
        
        self.mapfile_csv_fieldnames = str.split(self.config.get("MAPFILE",'fieldnames'), sep=",")
        
        self.log.debug(self.mapfile_csv_fieldnames)

        # parse csv to list        
        self.mapfile_csv_list = MapfileUtils.parse_csv_to_list(self.config.get('MAPFILE','location'), 
        self.mapfile_csv_fieldnames, delimiter=';')

        message = "Found mapfile on path {}: Items in path: {}".format(self.config.get("MAPFILE", "location"), 
        str(len(self.mapfile_csv_list)))

        return message

    def gather_valid_docs_in_solr(self):
        self.log.info("Gathering valid docs from SOLR.")
        
        # Get total hits
        total_hits = self.solr.search(self.config.get('SOLR', 'replace_query'),
        fl=self.config.get('SOLR','gathered_fields'), sort='search.uniqueid ASC', rows=0)

        self.log.info("Found {} docs ".format(total_hits.hits))
        
        # store a solr.search iterator
        self.gathered_docs = self.solr.search(self.config.get('SOLR', 'replace_query'),
        fl=self.config.get('SOLR','gathered_fields'), sort='search.uniqueid ASC',
        cursorMark='*')
        
        message = "Found {} docs and stored the in {}".format(str(total_hits.hits), type(self.gathered_docs).__name__)
        
        return message

    def preprocess_solr_docs(self, doc):
        
        self.log.info("Preprocessing SOLR doc {}.".format(doc['handle']))

        if SolrUtils.doc_id_count_valid(doc, 
        [self.config.get('SOLR','old_id_fieldname'), self.config.get('SOLR','new_id_fieldname')]) is False:
                    
            # add reason to solr doc dict to be used for reporting
            doc['reason'] = 'count_invalid'
            
            message = ReportingUtils.create_doc_error_message(doc, self.config.get('WORKFLOW','error_report_fields'))
            raise Exception(message) 

        self.log.debug(str.split(self.config.get('SOLR', 'gathered_fields'), sep=','))
        SolrUtils.preproces_doc_fields(doc, 'handle',
        str.split(self.config.get('SOLR', 'gathered_fields'), sep=','))

        if SolrUtils.old_lis_id_found(doc, self.config.get('LIS', 'old_id_regex'),
        [self.config.get('SOLR','old_id_fieldname'),self.config.get('SOLR', 'new_id_fieldname')]) is False:
            
            doc['reason'] = 'invalid_id_in_solr'
            
            message = ReportingUtils.create_doc_error_message(doc, self.config.get('WORKFLOW','error_report_fields'))

            raise Exception(message)

        message = "Doc {} preprocessed.".format(doc['handle'])
        
        return message
    
    def compare_solr_to_mapfile(self, doc):

        self.log.info("Trying to replace {} for {} in doc {} based on mapfile.".format(self.config.get('LIS','old_id_name'),
        self.config.get('LIS','new_id_name'), doc['handle']))

        old_id = SolrUtils.get_old_id(doc, 
        [self.config.get('SOLR', 'old_id_fieldname'), self.config.get('SOLR','new_id_fieldname')])
        
        self.log.info("Doc {} has old_id: {}. Looking for it in mapfile.".format(doc['handle'], old_id))

        id_found_in_mapfile = False
        j = 0
        for row in self.mapfile_csv_list:
            
            if MapfileUtils.find_id_in_column(row, self.config.get('LIS', 'old_id_name'), old_id) is True:
                
                id_found_in_mapfile = True
                self.log.info("Doc {} found in mapfile line {} / {}".format(doc['handle'], j, len(self.mapfile_csv_list)))
                
                # set SOLR doc 'dc.identifier.lisID' to a value of alma_id in that row
                doc[self.config.get('SOLR', 'new_id_fieldname')] = row[self.config.get('LIS','new_id_name')]
                
                self.log.info("Doc {}: {}: {} replaced by {}: {}\n".format(doc['handle'], 
                self.config.get('LIS','old_id_name'), old_id, self.config.get('LIS','new_id_name'), 
                doc[self.config.get('SOLR','new_id_fieldname')]))
                
                # when correct alma_id is assigned to doc['dc.identifier.lisID], remove that item from mapfile list -> speed up lookup of subsequent items
                self.mapfile_csv_list.pop(j)

                break
            
            j += 1
            
        if id_found_in_mapfile is False:
            doc['reason'] = 'not_found_in_mapfile'
            
            message = ReportingUtils.create_doc_error_message(doc, 
            str.split(self.config.get('WORKFLOW','error_report_fields'), sep=','))
            
            raise ValueError(message)
        
        message = "Doc {}: old id {} {} replaced by new id {} {}".format(doc['handle'], 
        self.config.get('LIS','old_id_name'), old_id, self.config.get('LIS', 'new_id_name'), 
        doc[self.config.get('SOLR','new_id_fieldname')])
        
        return message 

    def prepare_record_updates(self, doc):

        self.log.info("Doc {}: Preparing record update url and payload for DSpace.".format(doc['handle']))

        doc['metadata_entry'] = self.dsapi.create_metadataentry_object(meta_dict=doc, meta_field='dc.identifier.lisID')

        doc['request_url'] = self.dsapi.create_request_url(endpoint='items', dso_identifier=doc['search.resourceid'])

        if doc['request_url'] is None:
            doc['reason'] = 'request_url_not_created'
            
            message = ReportingUtils.create_doc_error_message(doc, self.config.get('WORKFLOW','error_report_fields'))

            raise ValueError(message)
        
        message = "Doc {}: record update url and payload created: request_url: {} \t medatata_entry: {}".format(
            doc['handle'], doc['request_url'], doc['metadata_entry'])

        return message

    
    def update_dspace_records(self, doc):
        
        self.log.info("Doc {}: Updating DSpace record.".format(doc['handle']))
        
        try:
            message = self.dsapi.request_update_metadata(doc['request_url'], doc['metadata_entry'])

            return message
        except Exception as e:
            doc['reason'] = 'update_failed'
            
            message = ReportingUtils.create_doc_error_message(doc, self.config.get('WORKFLOW','error_report_fields'))
            
            raise Exception(message)
