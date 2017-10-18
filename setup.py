from distutils.core import setup


setup( name = "groot",
       version = "0.0.0.1",
       description = "Generate N-rooted fusion graphs from genomic data.",
       author = "Martin Rusilowicz",
       long_description = open( "readme.md" ).read(),
       license = "GPLv3",
       packages = [ "groot" ],
       )
