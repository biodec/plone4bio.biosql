def list_bioentry_accessions(self, dbid):
    self.cursor.execute(
        "SELECT accession FROM bioentry WHERE biodatabase_id = %s",
        (dbid,))
    for rv in self.cursor.fetchall():
        yield "%s" % (rv[0])

def list_bioentry_versions(self, dbid):
    self.cursor.execute(
        "SELECT accession, version FROM bioentry WHERE biodatabase_id = %s",
        (dbid,))
    for rv in self.cursor.fetchall():
        if rv[1] == 0:
            yield "%s" % (rv[0])
        else:
            yield "%s.%s" % (rv[0], rv[1])
