
from Acquisition import aq_inner

from zope.component import createObject
from zope.formlib import form
from zope.app.form.browser.textwidgets import TextWidget
from Products.Five.browser import BrowserView

from plone.app.form import base

from plone4bio.base import Plone4BioMessageFactory as _
from plone4bio.base.browser.seqrecord import SeqRecordAddForm
from plone4bio.base.content.seqrecord import SeqRecord
from plone4bio.biosql.interfaces import IBioSQLRoot, IBioSQLDatabase, IBioSQLSeqRecord

class LongTextWidget(TextWidget):
    displayWidth = 50

class BioSQLRootAddForm(base.AddForm):
    """Add form """
    form_fields = form.Fields(IBioSQLRoot)
    form_fields['dsn'].custom_widget = LongTextWidget
    label = _(u"Add BioSQLRoot")
    form_name = _(u"Edit BioSQLRoot")
    def create(self, data):
        object = createObject(u"plone4bio.biosql.BioSQLRoot")
        form.applyChanges(object, self.form_fields, data)
        return object

class BioSQLRootEditForm(base.EditForm):
    """Edit form """
    form_fields = form.Fields(IBioSQLRoot)
    form_fields['dsn'].custom_widget = LongTextWidget
    label = _(u"Edit BioSQLRoot")
    form_name = _(u"Edit BioSQLRoot")

class RefreshCatalog(BrowserView):
    """View"""
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.clear = 1

    def __call__(self):
        self.context.refreshCatalog(clear=self.clear)
        self.request.response.redirect('@@view')

