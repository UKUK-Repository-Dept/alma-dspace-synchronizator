from __future__ import annotations
import typing

if typing:
    import pysolr

def test_solr(solr_instance: pysolr.Solr):

    return solr_instance.ping()