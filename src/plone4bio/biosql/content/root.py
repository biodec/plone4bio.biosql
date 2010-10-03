# -*- coding: utf-8 -*-
__author__ = '''Mauro Amico <mauro@biodec.com>'''
__docformat__ = 'plaintext'

from threading import local
from zope.interface import implements
from zope.component.factory import Factory
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleVocabulary


from Acquisition import aq_base

from plone.app.content.container import Container
# from plone.memoize import request
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.interfaces.constrains import IConstrainTypes

from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from Products.Archetypes import atapi

from Products.Archetypes import atapi
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import registerType

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

"""

class BioSQLRoot(Container):
    portal_type='BioSQLRoot'

    implements(IBioSQLRoot, IContainer, IFolderish, INameFromTitle)

    security = ClassSecurityInfo()
    # isPrincipiaFolderish = True # already on Container
    # dsn = FieldProperty(IBioSQLRoot['dsn'])
    dsn = 'postgres://postgres@localhost/plone4bio'
    seqrecord_key = FieldProperty(IBioSQLRoot['seqrecord_key'])
    _v_thread_local = local()

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('parent'):
            parent = kwargs['parent']
            del(kwargs['parent'])
        super(BioSQLRoot, self).__init__(*args, **kwargs)
"""


Plone4BioSchema = ATContentTypeSchema.copy() + atapi.Schema((
    atapi.StringField("dsn",
        required = True,
        widget = atapi.StringWidget(
            label = "dsn",
            label_msgid = "dsn_label",
            description = "DSN "
                          "... "
                          "...",
            description_msgid = "dsn_help",
            i18n_domain = "plone4bio")
    ),
    atapi.StringField("seqrecord_key",
        required = True,
        enforceVocabulary = True,
        default = 'bioentry_id',
        vocabulary = [("bioentry_id", _(u"bioentry_id")),
                      ("accession", _(u"accession")),
                      ("version", _(u"accession.version")),
                     ],
        widget = atapi.SelectionWidget(
            label = "seqrecord_key",
            label_msgid = "seqrecord_key_label",
            description = _(u"select the field name key for seqrecord uris"),
            description_msgid = "seqrecord_key_help",
            i18n_domain = "plone4bio")
    ),
    ))

class BioSQLRoot(ATCTContent):
    portal_type='BioSQLRoot'

    implements(IBioSQLRoot, IConstrainTypes)

    security = ClassSecurityInfo()
    schema = Plone4BioSchema
    _at_rename_after_creation = True
    isPrincipiaFolderish = True 
    # dsn = atapi.ATFieldProperty('dsn')
    dsn = 'postgres://postgres@localhost/plone4bio'
    seqrecord_key = "version"
    _v_thread_local = local()

    # XXX
    def getLocallyAllowedTypes(self):
        return []

    # see CMFPlone/CatalogTool.py
    def refreshCatalog(self, clear=1):
        return
        def indexObject(obj, path):
            if (base_hasattr(obj, 'indexObject') and
                safe_callable(obj.indexObject)):
                try:
                    obj.indexObject()
                except TypeError:
                    # Catalogs have 'indexObject' as well, but they
                    # take different args, and will fail
                    pass
                except: # CatalogError:
                    # import pdb; pdb.set_trace()
                    # obj.indexObject()
                    logger.exception("indexObject %r for %r" % (obj, self))
        for database in self.values():
            database.invalidateCache()
        portal_catalog = getToolByName(self, 'portal_catalog')
        for obj in portal_catalog.searchResults(path=self.absolute_url_path()):
            portal_catalog.uncatalog_object(obj.getPath())
        portal_catalog.ZopeFindAndApply(self, search_sub=True, apply_func=indexObject)

    """
    def __getattr__(self, name):
        if self.has_key(name):
            return self[name]
        else:
            raise AttributeError, name
    """

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
        dbserver = getattr(self._v_thread_local, 'dbserver', None)
        if dbserver is None or not dbserver.adaptor.conn.is_valid:
            try:
                wrapper = getSAWrapper(self.dsn)
            except ValueError:
                wrapper = createSAWrapper(dsn=self.dsn, name=self.dsn)
            #TODO: manage OperationalError on connection
            dbserver = DBServer(wrapper.connection, __import__(drivers[self.dsn.split(':')[0]]))
            self._v_thread_local.dbserver = dbserver
        return dbserver

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
        if not dbserver:
            raise StopIteration
        for name in dbserver.keys():
            yield str(name)
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

    def __bobo_traverse__(self, REQUEST, name):
        try:
            return self[name]
        except KeyError:
            pass        
        if hasattr(aq_base(self), name):
            return getattr(self, name)
        # webdav
        """
        method = REQUEST.get('REQUEST_METHOD', 'GET').upper()
        if (method not in ('GET', 'POST') and not
              isinstance(REQUEST.RESPONSE, xmlrpc.Response) and
              REQUEST.maybe_webdav_client and not REQUEST.path):
            return ReflectoNullResource(self, name, REQUEST).__of__(self)
        """
        return ATCTContent.__bobo_traverse__(self, REQUEST, name)

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

atapi.registerType(BioSQLRoot, 'plone4bio.biosql')

