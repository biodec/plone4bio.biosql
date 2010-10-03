import logging
logger = logging.getLogger("plone4bio.biosql")
logger.debug('Start initialization of product.')

from Products.CMFCore import utils as cmfutils

from Products.CMFCore import DirectoryView
from Products.Archetypes.atapi import process_types
from Products.Archetypes import listTypes

from config import PROJECTNAME
from config import DEFAULT_ADD_CONTENT_PERMISSION
from config import ADD_CONTENT_PERMISSIONS
from config import product_globals

from zope.i18nmessageid import MessageFactory
Plone4BioMessageFactory = MessageFactory('plone4bio')


class Plone4BioException(Exception):
    pass

def initialize(context):
    """Intializer called when used as a Zope 2 product."""
    # imports packages and types for registration
    import interfaces
    import content

    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types=all_content_types,
        permission=DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors=all_constructors,
        fti=all_ftis,
        ).initialize(context)

    # Give it some extra permissions to control them on a per class limit
    for i in range(0, len(all_content_types)):
        klassname = all_content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type=all_ftis[i]['meta_type'],
                              constructors=(all_constructors[i],),
                              permission=ADD_CONTENT_PERMISSIONS[klassname])
