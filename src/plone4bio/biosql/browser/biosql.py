
from Acquisition import aq_inner

from zope.component import createObject
from zope.formlib import form
from zope.app.form.browser.textwidgets import TextWidget

from plone.app.form import base

from plone4bio.base import Plone4BioMessageFactory as _
from plone4bio.base.browser.seqrecord import SeqRecordAddForm
from plone4bio.base.content.seqrecord import SeqRecord
from plone4bio.biosql.interfaces import IBioSQLRoot, IBioSQLDatabase, IBioSQLSeqRecord

class BioSQLDatabaseAddForm(base.AddForm):
    """Add form """
    form_fields = form.Fields(IBioSQLDatabase)
    label = _(u"Add BioSQLDatabase")
    form_name = _(u"Edit BioSQLDatabase")
    def create(self, data):
        root = self.context.getBioSQLRoot()
        dbserver = root.getDBServer()
        biodb = dbserver.new_database(data['id'], description=data.get("description", None))
        dbserver.commit()
        object = root[data['id']]
        # TODO: test catalog object
        return object

class BioSQLDatabaseEditForm(base.EditForm):
    """Edit form """
    form_fields = form.Fields(IBioSQLDatabase)
    label = _(u"Edit BioSQLDatabase")
    form_name = _(u"Edit BioSQLDatabase")

class BioSQLSeqRecordEditForm(base.EditForm):
    """Edit form """
    form_fields = form.Fields(IBioSQLSeqRecord)
    label = _(u"Edit BioSQLSeqRecord")
    form_name = _(u"Edit BioSQLSeqRecord")

class BioSQLSeqRecordAddForm(SeqRecordAddForm):
    """Add form """
    label = _(u"Add BioSQLSeqRecord")
    form_name = _(u"Edit BioSQLSeqRecord")
    def create(self, data):
        seqrecord = SeqRecord(title=data['title'])
        form.applyChanges(seqrecord, self.form_fields, data)
        # TODO: id policy
        seqrecord.id = seqrecord.title
        # root = self.context.getBioSQLRoot()
        # dbserver = root.getDBServer()
        db = aq_inner(self.context.context)
        biodb = db.getDatabase(reload=True)
        # aq_inner(self.context.context).getDatabase().adaptor.conn.is_valid
        # dbserver.adaptor.conn.is_valid
        if biodb.load([seqrecord.seqrecord,]) == 1:
            bioentry_id = biodb.adaptor.last_id('bioentry')
            biodb.adaptor.commit()
            db.keys(reload=True)
            obj = db[str(bioentry_id)]
            obj._getSeqRecord(reload=True)
        else:
            obj = None
        return obj

