__author__ = '''Mauro Amico <mauro@biodec.com>'''
__docformat__ = 'plaintext'

import traceback

from zope.interface import implements
from zope.component import adapts
from zope.component.factory import Factory
from plone.app.content.batching import IBatch
from Products.CMFCore.interfaces import IFolderish
from zope.app.container.interfaces import IContainer
from plone.app.content.container import Container

from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
# from Products.CMFPlone.interfaces.ConstrainTypes \
#        import IConstrainTypes as Z2IConstrainTypes
# from Products.CMFPlone.interfaces.constrains import IConstrainTypes
from AccessControl.Permissions import access_contents_information
from UserDict import DictMixin

# BioPython
from Bio import GenBank

# Plone4Bio
from plone4bio.base import Plone4BioMessageFactory as _
from plone4bio.biosql.interfaces import IBioSQLDatabase
from plone4bio.biosql.content.proxy import BaseProxy
from plone4bio.biosql.content.seqrecord import BioSQLSeqRecord

def _cachekey(method, self):
    return (method.__name__, self.absolute_url_path())

class BioSQLDatabase(BaseProxy, DynamicType, Container):
    """  BioSQLDatabase ... """
    __implements__ = (DynamicType.__implements__)
    implements(IBioSQLDatabase, IContainer, IFolderish)
    adapts(IBatch)
    meta_type = "BioSQLDatabase"
    portal_type = "BioSQLDatabase"
    security = ClassSecurityInfo()
    isPrincipiaFolderish = True
    _v_database = None
    _v_keys = None
    #_v_root = None

    #def __init__(self, *args, **kwargs):
    #    if kwargs.has_key('parent'):
    #         self._v_root = kwargs['parent']
    #         del(kwargs['parent'])
    #    super(BioSQLDatabase, self).__init__(*args, **kwargs)

    # @ram.cache(_cachekey)
    def getDatabase(self, reload=False):
        if self._v_database:
            if not self._v_database.adaptor.conn.is_valid:
                #TODO: logging
                self._v_database = None
        if self._v_database is None or reload:
            self._v_keys = None
            dbserver = self.getBioSQLRoot().getDBServer()
            try:
                self._v_database = dbserver[self.id]
            except KeyError:
                self._v_database = None
        return self._v_database

    # @property
    def name(self):
        return self.id

    # TODO: ....
    def loadData(self, data, dbtype):
        if (dbtype == "GenBank"):
            # get the GenBank file we are going to put into it
            parser = GenBank.FeatureParser()
            iterator = GenBank.Iterator(data, parser)
            # finally put it in the database
            try:
                self.getDatabase().load(iterator)
            except:
                self.getBioSQLRoot().getDBServer().adaptor.conn.rollback()
                return traceback.format_exc()
            self.getBioSQLRoot().getDBServer().adaptor.conn.commit()
            return ""
        else:
            raise "Unknown dbtype: %r" % (dbtype) 

    security.declareProtected(View, "getValues")
    def getValues(self): 
        for k in self.__iter__():
            yield self[k]
   
    def __len__(self):
        # return len(self.keys())
        db = self.getDatabase()
        if db:
            return len(db.keys())
        return 0

    security.declareProtected(View, "getLength")
    def getLength(self):
        return self.__len__()
 
    # IReadContainer implementation based on DictMixin
    def __getitem__(self, key):
        if not self.has_key(key):            
            raise KeyError(key)
        klass = BioSQLSeqRecord
        obj = klass(key).__of__(self)
        return obj

    def __iter__(self):
        # TODO: cache?
        try:
            database = self.getDatabase()
        except AttributeError:
            # No acquisition context, fail silently
            raise StopIteration
        if not database:
            raise StopIteration
        for name in database.get_all_primary_ids(): # -- bioentry_id
            yield str(name)
    
    def keys(self, reload=False):
        # TODO: check cache invalidation
        # self._v_keys = list(self.__iter__())
        if self._v_keys is None or reload:
            self._v_keys = list(self.__iter__())
        return self._v_keys
            
    # XXX verificare .....
    def has_key(self, key):
        if not isinstance(key, basestring):
            return False
        try:
            key = int(key)
        except ValueError:
            return False
        try:
            database = self.getDatabase()
        except AttributeError:
            # No acquisition context, fail silently
            return False
        # TODO: bug in get_Seq_by_primary_id ??? see #XXX
        if database.get_Seq_by_primary_id(key):
            return True
        else:
            return False
        # return key in [str(id) for id in self.keys()]
        #try:
        #    return key in self.keys()
        #except:
        #    return False
    
    # Acquisition wrappers don't support the __iter__ slot, so re-implement
    # iteritems to call __iter__ directly.
    def iteritems(self):
        for k in self.__iter__():
            yield (k, self[k])

    ########################################################################
    # ObjectManager implementation
    security.declareProtected(access_contents_information, 'objectIds')
    def objectIds(self, spec=None):
        # Returns a list of subobject ids of the current object.
        # If 'spec' is specified, returns objects whose meta_type
        # matches 'spec'.
        assert spec is None, 'spec argument unsupported'
        return self.__iter__()

    security.declareProtected(access_contents_information, 'objectValues')
    def objectValues(self, spec=None):
        # Returns a list of actual subobjects of the current object.
        # If 'spec' is specified, returns only objects whose meta_type
        # match 'spec'.
        assert spec is None, 'spec argument unsupported'
        return self.itervalues()

    security.declareProtected(access_contents_information, 'objectItems')
    def objectItems(self, spec=None):
        # Returns a list of (id, subobject) tuples of the current object.
        # If 'spec' is specified, returns only objects whose meta_type match
        # 'spec'
        assert spec is None, 'spec argument unsupported'
        return self.iteritems()

# mix in selected methods from DictMixin
# We don't want *everything* because some cause problems for us
for m in ('__contains__', 'iterkeys', 'itervalues', 'values', 'items', 'get'):
    setattr(BioSQLDatabase, m, getattr(DictMixin, m).im_func)
    
InitializeClass(BioSQLDatabase)

bioSQLDatabaseFactory = Factory(BioSQLDatabase, title=_(u"Create a new BioSQL Database"))

