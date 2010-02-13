import unittest
from Testing import ZopeTestCase as ztc
from plone4bio.biosql.tests.base import BaseTestCase


def test_suite():
    return unittest.TestSuite([
        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
                'README.txt', package='plone4bio.biosql',
                test_class=BaseTestCase),
        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

