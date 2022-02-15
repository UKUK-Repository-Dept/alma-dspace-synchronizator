import pysolr
from . import test
from configparser import ConfigParser, ExtendedInterpolation

config = ConfigParser(interpolation=ExtendedInterpolation())

print(config)

try:
    config.read('dspace_solr/solr_config.ini')
except Exception as e:
    raise e

solr_connection = config.get('GENERAL','hostname') + config.get('GENERAL','core')

solr = pysolr.Solr(solr_connection)

try:
    solr.ping()
except Exception as e:
    raise e
