import csv

from requests import request
from . import Workflow
from utility import FileUtils, SolrUtils, MapfileUtils

class ReplaceWorkflow(Workflow):

    def find_input_file(self):

        self.log.info("{} - Trying to find and parse mapfile.".format(self.__class__.__name__ ))
        
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

        mapfile_list = list()
        
        self.mapfile_csv_fieldnames = str.split(self.config.get("MAPFILE",'fieldnames'), sep=",")
        
        self.log.debug(self.mapfile_csv_fieldnames)
        
        with open(self.config.get('MAPFILE','location'), encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file, fieldnames=self.mapfile_csv_fieldnames, delimiter=";")  
            
            mapfile_list = [row for row in csv_reader]
            self.mapfile_csv_list = mapfile_list
        
        message = "Found mapfile on path " + self.config.get("MAPFILE", "location") \
        + ": Items in path: " + str(len(self.mapfile_csv_list))

        return message

    def gather_valid_docs_in_solr(self):
        self.log.info("{} - Gathering valid docs from SOLR.".format(self.__class__.__name__ ))
        
        # Get total hits
        total_hits = self.solr.search('(dc.identifier.aleph:* OR dc.identifier.lisID:0*) AND -dc.identifier.lisID:9*', 
        fl='search.uniqueid,search.resourceid,dc.identifier.aleph,dc.identifier.lisID,handle', sort='search.uniqueid ASC', rows=0)

        self.log.info("Found {} docs ".format(total_hits.hits))
        
        # store a solr.search iterator
        self.gathered_docs = self.solr.search('(dc.identifier.aleph:* OR dc.identifier.lisID:0*) AND -dc.identifier.lisID:9*',
        fl='search.uniqueid,search.resourceid,dc.identifier.aleph,dc.identifier.lisID,handle', sort='search.uniqueid ASC',
        cursorMark='*')
        
        message = "Found {} docs and stored the in {}".format(str(total_hits.hits), type(self.gathered_docs).__name__)
        # result = "ReplaceWorkflow - gather_valid_docs_in_solr - DONE"
        return message

    def preprocess_solr_docs(self, doc):
        
        self.log.info("{} - Preprocessing SOLR doc {}.".format(self.__class__.__name__, doc['handle']))

        if SolrUtils.doc_id_count_valid(doc, 
        [self.config.get('DSPACE','old_id_fieldname'), self.config.get('DSPACE','new_id_fieldname')]) is False:
                    
            # add reason to solr doc dict to be used for reporting
            doc['reason'] = 'count_invalid'
            # print(doc['reason'])
            # self.to_report_docs = (doc['search.uniqueid'], doc)
            message = '{};{};{};{}'.format(doc[self.config.get('DSPACE','old_id_fieldname')],
            doc[self.config.get('DSPACE','new_id_fieldname')], doc['handle'],doc['reason'])
            raise Exception(message)
            
            

        SolrUtils.preproces_doc_ids(doc, 'handle', 
        [self.config.get('DSPACE', 'old_id_fieldname'), self.config.get('DSPACE', 'new_id_fieldname')])

        if SolrUtils.old_lis_id_found(doc, self.config.get('LIS', 'old_id_regex'),
        [self.config.get('DSPACE','old_id_fieldname'),self.config.get('DSPACE', 'new_id_fieldname')]) is False:
            
            doc['reason'] = 'invalid_id_in_solr'
            # print(doc['reason'])
            message = '{};{};{};{}'.format(doc[self.config.get('DSPACE','old_id_fieldname')],
            doc[self.config.get('DSPACE','new_id_fieldname')], doc['handle'],doc['reason'])

            raise Exception(message)
        
        # self.to_process_docs = (doc['search.uniqueid'], doc)

        message = self.__class__.__name__ + ": Doc " + doc['handle'] + " preprocessed."
        
        return message
    
    def compare_solr_to_mapfile(self, doc):

        self.log.info("{} - Trying to replace {} for {} in doc {} based on mapfile.".format(self.__class__.__name__, 
        self.config.get('LIS','old_id_name'), self.config.get('LIS','new_id_name'), doc['handle']))

        old_id = SolrUtils.get_old_id(doc, 
        [self.config.get('DSPACE', 'old_id_fieldname'), self.config.get('DSPACE','new_id_fieldname')])
        
        self.log.info("{} - Doc {} has old_id: {}. Looking for it in mapfile.".format(self.__class__.__name__, 
        doc['handle'], old_id))

        id_found_in_mapfile = False
        j = 0
        for row in self.mapfile_csv_list:
            
            if MapfileUtils.find_id_in_column(row, self.config.get('LIS', 'old_id_name'), old_id) is True:
                
                id_found_in_mapfile = True
                self.log.info("{} - Doc {} found in mapfile line {} / {}".format(self.__class__.__name__,
                doc['handle'], j, len(self.mapfile_csv_list)))
                
                # set SOLR doc 'dc.identifier.lisID' to a value of alma_id in that row
                doc[self.config.get('DSPACE', 'new_id_fieldname')] = row[self.config.get('LIS','new_id_name')]
                
                self.log.info("{} - Doc {}: {}: {} replaced by {}: {}\n".format(self.__class__.__name__, doc['handle'], 
                self.config.get('LIS','old_id_name'), old_id, self.config.get('LIS','new_id_name'), 
                doc[self.config.get('DSPACE','new_id_fieldname')]))
                
                # when correct alma_id is assigned to doc['dc.identifier.lisID], remove that item from mapfile list -> speed up lookup of subsequent items
                self.mapfile_csv_list.pop(j)

                break
            
            j += 1
            
        if id_found_in_mapfile is False:
            doc['reason'] = 'not_found_in_mapfile'
            
            message = '{};{};{};{}'.format(doc[self.config.get('DSPACE','old_id_fieldname')],
            doc[self.config.get('DSPACE','new_id_fieldname')], doc['handle'],doc['reason'])
            
            raise ValueError(message)
        
        message = "{} - Doc {}: old id {} {} replaced by new id {} {}".format(self.__class__.__name__, doc['handle'], 
        self.config.get('LIS','old_id_name'), old_id, self.config.get('LIS', 'new_id_name'), 
        doc[self.config.get('DSPACE','new_id_fieldname')])
        
        return message 

    def prepare_record_updates(self, doc):

        self.log.info("{} - Doc {}: Preparing record update url and payload for DSpace.".format(self.__class__.__name__, 
        doc['handle']))

        doc['metadata_entry'] = self.dsapi.create_metadataentry_object(meta_dict=doc, meta_field='dc.identifier.lisID')

        doc['request_url'] = self.dsapi.create_request_url(endpoint='items', dso_identifier=doc['search.resourceid'])

        if doc['request_url'] is None:
            message = "Doc {}: request_url cannot be None. \
            Request URL was not created for some reason.".format(doc['handle'])
            doc['reason'] = 'request_url_not_created'
            
            message = '{};{};{};{}'.format(doc[self.config.get('DSPACE','old_id_fieldname')],
            doc[self.config.get('DSPACE','new_id_fieldname')], doc['handle'],doc['reason'])

            raise ValueError(message)
        
        message = "Doc {}: record update url and payload created: request_url: {} \t medatata_entry: {}".format(doc['handle'],
        doc['request_url'], doc['metadata_entry'])

        return message

    
    def update_dspace_records(self, doc):
        
        self.log.info("{} - Doc {}: Updating DSpace record.".format(self.__class__.__name__, doc['handle']))
        
        try:
            message = self.dsapi.request_update_metadata(doc['request_url'], doc['metadata_entry'])

            return message
        except Exception as e:
            doc['reason'] = 'update_failed'
            
            message = '{};{};{};{}'.format(doc[self.config.get('DSPACE','old_id_fieldname')],
            doc[self.config.get('DSPACE','new_id_fieldname')], doc['handle'],doc['reason'])
            
            raise Exception(message)
