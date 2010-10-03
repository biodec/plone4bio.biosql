
from zope.component import createObject
from zope.formlib import form
from zope.app.form.browser.textwidgets import TextWidget
from Products.Five.browser import BrowserView

from plone.app.form import base

from plone4bio.base import Plone4BioMessageFactory as _
from plone4bio.biosql.interfaces import IBioSQLRoot

class LongTextWidget(TextWidget):
    displayWidth = 50

class RefreshCatalog(BrowserView):
    """View"""
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.clear = 1

    def __call__(self):
        self.context.refreshCatalog(clear=self.clear)
        self.request.response.redirect('@@view')

