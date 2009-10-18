from setuptools import setup, find_packages
version = '1.0.1'

tests_require = ['collective.testcaselayer']

setup(name='plone4bio.biosql',
      version=version,
      description="Plone4Bio BioSQL",
      long_description='\n'.join(
          open(os.path.join(*path)).read() for path in [
              ("README.txt"),
              ("src", "plone4bio", "biosql", "README.txt"),
              ("docs", "AUTHORS.txt"), ("docs", "CHANGES.txt")]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Mauro Amico',
      author_email='mauro@biodec.com',
      url='http://www.biodec.com',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['plone4bio'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'z3c.sqlalchemy',
          'collective.monkeypatcher',
      ],
      tests_require=tests_require,
      extras_require={'tests': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
