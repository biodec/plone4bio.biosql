from zope.interface import implements
from Products.Five.browser import BrowserView
# from Products.CMFPlone import Batch
from interfaces import IBioSQLDatabaseView

class BioSQLDatabaseView(BrowserView):
    """ """
    implements(IBioSQLDatabaseView)

