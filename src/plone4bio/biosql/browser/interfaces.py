__author__ = """Mauro Amico <amico@biodec.com>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope import schema

class IBioSQLDatabaseView(Interface):
        """ Marker interface for ... """

class IBioSQLGeneView(Interface):
        """ Marker interface for ... """

class IBioSQLSeqRecordView(Interface):
        """ Marker interface for ... """

class IBioSQLRootView(Interface):
        """ Marker interface for a BioSQLRoot """
        
class IBioSQLRootLoad(Interface):
    """ """
    dbtype = schema.Choice(
                   title=u"dbtype",
                   description=u"Database type ...",
                   values=['GenBank', 'Fasta'],
                   default='GenBank')
