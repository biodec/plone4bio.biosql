from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from plone4bio.base import Plone4BioMessageFactory as _
from plone4bio.base.interfaces import ISeqRecord

class IBioSQLProxy(Interface):
    """A reflecto proxied filesystem object."""

    def getBioSQLRoot(self):
        """ Return BioSQLRoot object.
        """

    #def getPathToBioSQLObjectParent():
    #    """Return a path from the reflex object to this proxy.
    #
    #    The path will be a tuple of strings.
    #    """

class IBioSQLDatabase(IBioSQLProxy):
    """ IReadContainer  """
    id = schema.TextLine(title=_(u"biodatabase_id"), required=True)
    # authority = schema.TextLine(title=_(u"authority"))
    description = schema.Text(title=_(u"description"))

class IBioSQLGene(IBioSQLProxy):
    """ IReadContainer  """

class IBioSQLSeqRecord(ISeqRecord, IBioSQLProxy):
    """ IReadContainer  """

class IBioSQLRoot(Interface):
    """ """
    title = schema.TextLine(title=_(u"title"))
    dsn = schema.TextLine(title=_(u"DSN"),
        description=_(u"database source name, i.e.: postgres://user@dbserver/dbname"),
    )
    seqrecord_key = schema.Choice(title=_("seqrecord_key"),
        description =_(u"select the field name key for seqrecord uris"),
        vocabulary = SimpleVocabulary.fromItems([
                     (_(u"bioentry_id"), "bioentry_id"),
                     (_(u"accession"), "accession"),
                     (_(u"accession.version"), "version"),])
     )
