.. -*-doctest-*-

Create biosqlroot
=================

Create a mockup for a biopython's biosql database:

  >>> import tempfile
  >>> import os
  >>> from BioSQL import BioSeqDatabase

  >>> (dbh, dbpath) = tempfile.mkstemp(suffix=".db")
  >>> server = BioSeqDatabase.open_database(driver = 'sqlite3', db = dbpath)
  >>> server.load_database_sql('biosqldb-sqlite.sql')
  >>> server.commit()
  >>> server.close()

Create a plone4bio's biosqlroot:

    >>> self.login()
    >>> self.setRoles(('Manager',))
    >>> self.portal.invokeFactory('BioSQLRoot', u'biosqlroot')
    'biosqlroot'
    >>> biosqlroot = getattr(self.portal, u'biosqlroot')
    >>> biosqlroot.dsn = u'postgres://user:pass@server:port/db'

Search catalog:
 
    >>> brains = self.portal_catalog.searchResults(portal_type='BioSQLSeqRecord', path=biosqlroot.path)
    >>> len(brains)
    5

    >>> os.unlink(dbpath)
