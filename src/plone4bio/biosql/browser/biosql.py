# -*- coding: utf-8 -*-
#
# File: biosql.py
#
# Copyright (c) 2010 by Mauro Amico (Biodec Srl)
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# @version $Revision: $:
# @author  $Author: $:
# @date    $Date: $:

__author__ = '''Mauro Amico <mauro@biodec.com>'''
__docformat__ = 'plaintext'

from Acquisition import aq_inner
from zope.formlib import form

from Products.Five.formlib.formbase import AddFormBase
from Products.Five.formlib.formbase import EditFormBase

from plone4bio.base import Plone4BioMessageFactory as _
from plone4bio.base.content.seqrecord import SeqRecord
from plone4bio.biosql.interfaces import IBioSQLDatabase, IBioSQLSeqRecord

class BioSQLDatabaseAddForm(AddFormBase):
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

class BioSQLDatabaseEditForm(EditFormBase):
    """Edit form """
    form_fields = form.Fields(IBioSQLDatabase)
    label = _(u"Edit BioSQLDatabase")
    form_name = _(u"Edit BioSQLDatabase")

class BioSQLSeqRecordEditForm(EditFormBase):
    """Edit form """
    form_fields = form.Fields(IBioSQLSeqRecord)
    label = _(u"Edit BioSQLSeqRecord")
    form_name = _(u"Edit BioSQLSeqRecord")

class BioSQLSeqRecordAddForm(AddFormBase):
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

