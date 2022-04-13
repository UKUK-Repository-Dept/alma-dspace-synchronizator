import os
import re

class FileUtils(object):

    @staticmethod
    def file_exists(path, is_remote=False, sftp_client=None):
        """
        Checks if file exists on local or remote path.
        :param path: path to file
        :param is_remote: bool - True if mapfiles are on remote location, False if they are on local location
        :param location:
        :return: bool - True if file exists, False otherwise
        """
        print("FileUtils: Checking if file", path, "exists.")
        if is_remote is True:
            if sftp_client is None:
                raise Exception('No SFTP client reference provided. Cannot check existence of remote file.')

            try:
                sftp_client.stat(path)
            except IOError as e:
                print(e)
                print("File", path, "not found on remote path.")
                return False

            return True
        else:
            # check if file exists on local machine
            if os.path.exists(path) and os.path.isfile(path):
                return True
            else:
                return False

class SolrUtils(object):

    @staticmethod
    def preproces_doc_ids(doc, main_id_field_name, id_field_names: list):
        
        for field_name in id_field_names:
            if field_name not in doc.keys():
                print("Doc {0} does not have {1}. Adding {1} with {2} value".format(doc[main_id_field_name], field_name, None))
                doc[field_name] = None
                continue
            else: 
                print("Doc {0} has field {1} of type {2}. Storing just as type {3}".format(doc[main_id_field_name],
                field_name, type(doc[field_name]), str.__name__))
                doc[field_name] = doc[field_name][0]

        return doc

    @staticmethod
    def doc_id_count_valid(doc, id_field_names: list):
        
        for field in id_field_names:
            print("Checking if doc {} does not have multiple occurences of field {}".format(doc['handle'], field))
            
            if field not in doc.keys():
                print("Doc {0} does not have field {1}. Will be fixed in later processing.".format(doc['handle'], field))
                continue

            if len(doc[field]) > 1:
                print("Doc {0} has multiple fields {1}. Doc {0} is invalid.".format(doc['handle'], field))
                return False
            
            else:
                # id count is 0 or 1
                print("Doc {0} has valid field {1} count.".format(doc['handle'], field))
                return True

    @staticmethod
    def old_lis_id_found(doc, old_id_regex, id_field_names: list):
        
        for field in id_field_names:
            print("Checking contents of the field {}".format(field), flush=False, end="\t")
            print("Content of the field is: {}\n".format(doc[field]))
            
            if doc[field] is None:
                continue
    
            if re.match('^' + old_id_regex + '$', doc[field]):
                return True
            else:
                return False

    @staticmethod
    def get_old_id(docs_dict, lookup_fields: list):
        old_id = None

        for field in lookup_fields:
            if docs_dict[field] is not None:
                old_id = docs_dict[field]
            
        
        return old_id

class MapfileUtils(object):

    @staticmethod
    def find_id_in_column(row, column_name, doc_identifier) -> bool:
        
        
        if row[column_name] == doc_identifier: # identifier in mapfile list is the same as identifier in SOLR doc
            print("{} found: {}".format(column_name, row['aleph_id']), flush=False, end="\t")
            
            return True
        else:
            return False