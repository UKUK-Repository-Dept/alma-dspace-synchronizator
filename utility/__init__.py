import os
import re
import logging
import csv

class FileUtils(object):

    __log = logging.getLogger(__name__)

    @classmethod
    def file_exists(cls, path, is_remote=False, sftp_client=None):
        """
        Checks if file exists on local or remote path.
        :param path: path to file
        :param is_remote: bool - True if mapfiles are on remote location, False if they are on local location
        :param location:
        :return: bool - True if file exists, False otherwise
        """
        cls.__log.info(cls.__name__)
        cls.__log.info("FileUtils: Checking if file {} exists.".format(path))
        if is_remote is True:
            if sftp_client is None:
                raise Exception('No SFTP client reference provided. Cannot check existence of remote file.')

            try:
                sftp_client.stat(path)
            except IOError as e:
                cls.__log.error("File", path, "not found on remote path.")
                cls.__log.error(e, exc_info=True)
                return False

            return True
        else:
            # check if file exists on local machine
            if os.path.exists(path) and os.path.isfile(path):
                return True
            else:
                return False


class SolrUtils(object):

    __log = logging.getLogger(__name__)

    @classmethod
    def preproces_doc_fields(cls, doc, main_id_field_name, id_field_names: list):
        
        for field_name in id_field_names:
            if field_name not in doc.keys():
                cls.__log.info("Doc {0} does not have {1}. Adding {1} with {2} value".format(doc[main_id_field_name], 
                field_name, None))
                doc[field_name] = None
                continue
            
            if type(doc[field_name]) is list:
                cls.__log.info("Doc {0} has field {1} of type {2}. Storing just as type {3}".format(doc[main_id_field_name],
                field_name, type(doc[field_name]), str.__name__))
                doc[field_name] = doc[field_name][0]

        return doc

    @classmethod
    def doc_id_count_valid(cls, doc, id_field_names: list):
        
        for field in id_field_names:
            cls.__log.info("Checking if doc {} does not have multiple occurences of field {}".format(doc['handle'], field))
            
            if field not in doc.keys():
                cls.__log.info("Doc {0} does not have field {1}. Will be fixed in later processing.".format(doc['handle'], field))
                continue

            if len(doc[field]) > 1:
                cls.__log.info("Doc {0} has multiple fields {1}. Doc {0} is invalid.".format(doc['handle'], field))
                return False
            
            else:
                # id count is 0 or 1
                cls.__log.info("Doc {0} has valid field {1} count.".format(doc['handle'], field))
                return True

    @classmethod
    def old_lis_id_found(cls, doc, old_id_regex, id_field_names: list):
        
        for field in id_field_names:
            cls.__log.info("Checking contents of the field {}".format(field))
            cls.__log.info("Content of the field is: {}\n".format(doc[field]))
            
            if doc[field] is None:
                continue
    
            if re.match('^' + old_id_regex + '$', doc[field]):
                return True
            else:
                return False

    @classmethod
    def get_old_id(cls, docs_dict, lookup_fields: list):
        old_id = None

        for field in lookup_fields:
            if docs_dict[field] is not None:
                old_id = docs_dict[field]
            
        
        return old_id

class MapfileUtils(object):

    __log = logging.getLogger(__name__)

    @classmethod
    def find_id_in_column(cls, row, column_name, doc_identifier) -> bool:
        
        
        if row[column_name] == doc_identifier: # identifier in mapfile list is the same as identifier in SOLR doc
            cls.__log.info("{} found: {}".format(column_name, row['aleph_id']))
            
            return True
        else:
            return False

    @classmethod
    def parse_csv_to_list(cls, filepath, fieldnames, delimiter):

        mapfile_list = list()

        try:
            with open(filepath, encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file, fieldnames, delimiter)  
                
                mapfile_list = [row for row in csv_reader]
            
            return mapfile_list

        except IOError as e:
            raise e

class ReportingUtils(object):

    __log = logging.getLogger(__name__)

    @classmethod
    def create_doc_error_message(cls, doc, reported_fields, report_type='csv'):

        cls.__log.info('Create error report message for doc {}'.format(doc))
        if report_type != 'csv':
            raise NotImplementedError
        
        else:
            doc_field_values = [doc[field] if doc[field] is not None else '' for field in reported_fields]
            doc_field_values.append(doc['reason'])
            message = ';'.join([value for value in doc_field_values])
        
        cls.__log.debug("Report message: {}".format(message))

        return message
        

