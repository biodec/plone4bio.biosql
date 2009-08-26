from zope.i18nmessageid import MessageFactory
Plone4BioMessageFactory = MessageFactory('plone4bio')

# Kick the permission definition
#import permissions

def initialize(context):
    """Intializer called when used as a Zope 2 product."""
