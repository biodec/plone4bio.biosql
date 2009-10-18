__author__ = '''Mauro Amico <mauro@biodec.com>'''
__docformat__ = 'plaintext'

from zope.interface import implements
from zope.component.factory import Factory
from zope.schema.fieldproperty import FieldProperty

from plone.app.content.container import Container
# from plone.memoize import request
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from zope.app.container.interfaces import IContainer
from plone.app.content.interfaces import INameFromTitle

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from AccessControl.Permissions import access_contents_information
from UserDict import DictMixin

from z3c.sqlalchemy import createSAWrapper, getSAWrapper
from sqlalchemy.exceptions import OperationalError

from BioSQL.BioSeqDatabase import DBServer

from plone4bio.base import Plone4BioMessageFactory as _
from plone4bio.biosql.interfaces import IBioSQLRoot
from plone4bio.biosql.content.database import BioSQLDatabase

import logging
logger = logging.getLogger('plone4bio')

_marker=[]

drivers = {
 'postgres' : 'psycopg2',
 'mysql' : 'MySQLdb',
}

def getdbkey(f, self, *args):
    return self.dsn

# WebDAV ... Collection
# class BioSQLRoot(BaseContent, BrowserDefaultMixin):
class BioSQLRoot(Container):
    __implements__ = (BrowserDefaultMixin.__implements__)
    portal_type='BioSQLRoot'
    implements(IBioSQLRoot, IContainer, IFolderish, INameFromTitle)
    security = ClassSecurityInfo()
    # isPrincipiaFolderish = True # already on Container
    dsn = FieldProperty(IBioSQLRoot['dsn'])
    seqrecord_key = FieldProperty(IBioSQLRoot['seqrecord_key'])
    _v_dbserver = None

    # see CMFPlone/CatalogTool.py
    def refreshCatalog(self, clear=1):
        def indexObject(obj, path):
            if (base_hasattr(obj, 'indexObject') and
                safe_callable(obj.indexObject)):
                try:
                    obj.indexObject()
                except TypeError:
                    # Catalogs have 'indexObject' as well, but they
                    # take different args, and will fail
                    pass
        for database in self.values():
            database.invalidateCache()
        portal_catalog = getToolByName(self, 'portal_catalog')
        for obj in portal_catalog.searchResults(path=self.absolute_url_path()):
            portal_catalog.uncatalog_object(obj.getPath())
        portal_catalog.ZopeFindAndApply(self, search_sub=True, apply_func=indexObject)

    def __getattr__(self, name):
        if self.has_key(name):
            return self[name]
        else:
            raise AttributeError, name

    security.declareProtected(View, "getBioSQLRoot")
    def getBioSQLRoot(self):
        return self

    def getpath(self, id):
        return str(id)

    # TODO: move to proxy ???
    # @request.cache(get_key=getdbkey, get_request='self.REQUEST')
    def getDBServer(self):
        if not self.dsn:
            return None
        if self._v_dbserver is None or not self._v_dbserver.adaptor.conn.is_valid:
            try:
                wrapper = getSAWrapper(self.dsn)
            except ValueError:
                wrapper = createSAWrapper(dsn=self.dsn, name=self.dsn)
            #TODO: manage OperationalError on connection
            self._v_dbserver = DBServer(wrapper.connection, __import__(drivers[self.dsn.split(':')[0]]))
        return self._v_dbserver

    security.declareProtected(View, "getValues")
    def getValues(self):
        for k in self.__iter__():
            yield self[k]
        
    # IReadContainer implementation based on DictMixin
    def __getitem__(self, key):
        if not self.has_key(key):            
            raise KeyError(key)
        class_ = BioSQLDatabase
        # obj = class_(key, parent=self).__of__(self)
        obj = class_(key).__of__(self)
        return obj

    def __iter__(self):
        try:
            dbserver = self.getDBServer()
        except AttributeError:
            # No acquisition context, fail silently
            raise StopIteration
        except OperationalError:
            logger.exception("getDBServer")
            raise StopIteration
        for name in dbserver.keys():
            yield name
        #try:
        #    for name in dbserver.keys():
        #        yield name
        #except: # InterfaceError:
        #    self._v_dbserver = None
        #    raise StopIteration

    def keys(self):
        return list(self.__iter__())
            
    def has_key(self, key):
        if not isinstance(key, basestring):
            return False
        for k in self.__iter__():
            if k == key:
                return True
        return False
    
    # Acquisition wrappers don't support the __iter__ slot, so re-implement
    # iteritems to call __iter__ directly.
    def iteritems(self):
        for k in self.__iter__():
            yield (k, self[k])

    # zope2/lib/python/OFS/ObjectManager.py
    def _getOb(self, id, default=_marker):
        # FIXME: what we really need to do here is ensure that only
        # sub-items are returned. That could have a measurable hit
        # on performance as things are currently implemented, so for
        # the moment we just make sure not to expose private attrs.
        if id[:1] != '_' and hasattr(self, id):
            return getattr(self, id)
        if self.has_key(id):
            return self[id]
        if default is _marker:
            raise AttributeError, id
        return default

    ########################################################################
    # ObjectManager implementation
    security.declareProtected(access_contents_information, 'objectIds')
    def objectIds(self, spec=None):
        # Returns a list of subobject ids of the current object.
        # If 'spec' is specified, returns objects whose meta_type
        # matches 'spec'.
        assert spec is None, 'spec argument unsupported'
        return self.keys()

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
    setattr(BioSQLRoot, m, getattr(DictMixin, m).im_func)

bioSQLRootFactory = Factory(BioSQLRoot, title=_(u"Create a new BioSQL Root"))
