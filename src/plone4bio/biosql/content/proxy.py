__author__ = '''Mauro Amico <mauro@biodec.com>'''
__docformat__ = 'plaintext'

import Acquisition

from zope.interface import implements
from plone.app.content.item import Item
# from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import notifyContainerModified
# from zope.event import notify
from OFS.subscribers import compatibilityCall
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Globals import InitializeClass

# ???
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.interfaces import ICatalogableDublinCore
from Products.CMFCore.interfaces import IDublinCore

# from plone4bio.base import Plone4BioMessageFactory as _
from plone4bio.biosql.interfaces import IBioSQLProxy, IBioSQLRoot

import logging
logger = logging.getLogger('plone4bio')

_marker=[]

class BaseProxy(CMFCatalogAware, Item, Acquisition.Implicit):
    meta_type="BioSQL proxy"
    implements(IBioSQLProxy, IDublinCore, ICatalogableDublinCore)
    security = ClassSecurityInfo()

    def __init__(self, key):
        self.id=key

    security.declareProtected(View, "getBioSQLRoot")
    def getBioSQLRoot(self):
        """Return our BioSQLRoot.
        """
        for parent in self.aq_inner.aq_chain:
            if parent is self.aq_base:
                continue
            if IBioSQLRoot.providedBy(parent):
                return parent
        raise RuntimeError('BioSQL object cannot exist outside an IBioSQLRoot '
                           'acquisition chain')

    def notifyWorkflowCreated(self):
        """ """
        pass

    # zope2/lib/python/OFS/ObjectManager.py
    def _setObject(self, id, object, roles=None, user=None, set_owner=1,
                   suppress_events=False):
        """Set an object into this container.
        Also sends IObjectWillBeAddedEvent and IObjectAddedEvent.
        """
        ob = object
        if not suppress_events:
            # notify(ObjectAddedEvent(ob, self, id))
            notifyContainerModified(self)
        compatibilityCall('manage_afterAdd', ob, ob, self)
        return id

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
# IDublinCore implementation

    def setTitle(self, title):
        if title == "":
            pass
        else:
            logger.warning("TODO: setTitle for %r - %r" % (self, title))
            
    def setDescription(self, description):
        self.setTitle(description)
            
    def Title(self):
        return self.getId()

    def Description(self):
        return self.description

    # def Date(self, zone=None):
    #     return self._statTime(ST_MTIME).ISO()

    def Type(self):
        return self.meta_type

    def Identifier(self):
        return self.absolute_url()

InitializeClass(BaseProxy)
