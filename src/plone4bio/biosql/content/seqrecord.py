__author__ = '''Mauro Amico <mauro@biodec.com>'''
__docformat__ = 'plaintext'

# from plone.memoize.instance import memoize
from zope.component.factory import Factory
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore.DynamicType import DynamicType

from plone4bio.base import Plone4BioMessageFactory as _
from plone4bio.base.content.seqrecord import SeqRecord
from plone4bio.base.interfaces import ISeqRecord
from plone4bio.biosql.content.proxy import BaseProxy
from plone4bio.biosql.interfaces import IBioSQLSeqRecord
from plone4bio.biosql.interfaces import IBioSQLDatabase

import logging
logger = logging.getLogger('plone4bio')

#TODO: move ....
"""
_marker = object()
class SeqRecordProperty(object):
    def __init__(self, name, default=_marker):
        self.__name = name
        self.__default = default

    def __get__(self, inst, klass):
        if inst is None:
            return self
        from stxnext import pdb;pdb.set_trace()
        ob = inst._getSeqRecord()
        for name in self.__name.split('.'):
            if not ob is _marker:
                try:
                    ob = ob.get(name, _marker)
                except:
                    ob = ob.__dict__.get(name, _marker)
        if ob is _marker:
            # TODO: manage defaults ????
            if not self.__default is _marker:
                return self.__default
            raise AttributeError(self.__name)
        return ob

    def __set__(self, inst, value):
        from stxnext import pdb;pdb.set_trace()
        try:
            inst.seqrecord.set(self.__name, value)
        except:
            logger.exception("unable to set %r on %r for %r" % (value, self.__name, inst))

    #def __getattr__(self, name):
    #    from stxnext import pdb;pdb.set_trace()
    #    return getattr(self.seqrecord, name)
"""


class BioSQLSeqRecord(BaseProxy, SeqRecord, DynamicType):
    """  BioSQLSeqRecord ... """
    __implements__ = (DynamicType.__implements__)
    implements(IBioSQLSeqRecord, ISeqRecord)
    meta_type = "BioSQLSeqRecord"
    portal_type = "BioSQLSeqRecord"
    security = ClassSecurityInfo()
    isPrincipiaFolderish = False
    _v_biodatabase = None
    _v_seqrecord = None

    #TODO: plone4bio.base
    def SearchableText(self):
        text = "%s %s %s %s" % (self.name, self.accessions, self.organism, self.description)
        for ref in self.references:
            text = "%s %s" % (text, ref)
        return text
    
    def Accession(self):
        return self.id
    accession = property(fget=Accession)
    
    def Name(self):
        return self._getSeqRecord().name
    name = property(fget=Name)
   
    #def Title(self):
    #    return self._getSeqRecord().name
    #title = property(fget=Title)
    
    def Sequence(self):
        return self._getSeqRecord().seq.data
    sequence = property(fget=Sequence)

    def Description(self):
        return self._getSeqRecord().description
    description = property(fget=Description) # SeqRecordProperty("description", u"")

    # TODO: refactoring
    # @memoize
    def _getSeqRecord(self, reload=False):
        """ """
        if self._v_seqrecord is None or reload:
            if self.getBioSQLRoot().seqrecord_key == 'accession':
                self._v_seqrecord = self._getBiodatabase().getDatabase().get_Seq_by_acc(self.id)
            elif self.getBioSQLRoot().seqrecord_key == 'version':
                self._v_seqrecord = self._getBiodatabase().getDatabase().get_Seq_by_ver(self.id)
            else: # default = 'bioentry_id':
                self._v_seqrecord = self._getBiodatabase().getDatabase()[self.id]
            logger.debug("%s -> %r" % (self.id, self._v_seqrecord))
        return self._v_seqrecord

    def _setSeqRecord(self, seqrecord):
        raise('seqrecord readonly')
    seqrecord = property(fget=_getSeqRecord, fset=_setSeqRecord)
    
    # @property
    def _getBiodatabase(self, reload=False):
        """Return our BioSQLDatabase.
        """
        # from stxnext import pdb;pdb.set_trace()
        if self._v_biodatabase is None or reload:
            for parent in self.aq_inner.aq_chain:
                if parent is self.aq_base:
                    continue
                if IBioSQLDatabase.providedBy(parent):
                    self._v_biodatabase = parent
                    return parent
            raise RuntimeError('BioSQLSeqRecord object cannot exist outside an IBioSQLDatabase '
                               'acquisition chain')
        return self._v_biodatabase
    def _setBiodatabase(self, seqrecord):
        raise('biodatabase readonly')
    biodatabase = property(fget=_getBiodatabase, fset=_setBiodatabase)

    # TODO: ???
    # def getURL(self, relative=0):
    #    """Generate a URL for this record"""
    #    return self.absolute_url(relative)

    def Annotations(self):
        return self._getSeqRecord().annotations
    annotations = property(fget=Annotations)
    
    def Features(self):
        return self._getSeqRecord().features
    features = property(fget=Features)

    def Dbxrefs(self):
        return self._getSeqRecord().dbxrefs
    dbxrefs = property(fget=Dbxrefs)

    def getReferences(self):
        return self.annotations['references']
    references = property(fget=getReferences)

    def getReferences(self):
        if self.annotations.has_key('references'):
            return self.annotations['references']
        else:
            return []
    references = property(fget=getReferences)

    def getOrganism(self):
        if self.annotations.has_key('organism'):
            return self.annotations['organism']
        else:
            return ""
    organism = property(fget=getOrganism)

    def getAccessions(self):
        if self.annotations.has_key('accessions'):
            return self.annotations['accessions']
        else:
            return ""
    accessions = property(fget=getAccessions)

    def getTaxonomy(self):
        if self.annotations.has_key('taxonomy'):
            return self.annotations['taxonomy']
        else:
            return []
    taxonomy = property(fget=getTaxonomy)


InitializeClass(BioSQLSeqRecord)

bioSQLSeqRecordFactory = Factory(BioSQLSeqRecord, title=_(u"Create a new BioSQL SeqRecord"))
