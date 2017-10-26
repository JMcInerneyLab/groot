from distutils.core import setup


setup( name = "groot",
       version = "0.0.0.2",
       description = "Generate N-rooted fusion graphs from genomic data.",
       author = "Martin Rusilowicz",
       license = "GPLv3",
       packages = [ "groot" ],
       entry_points= { "console_scripts": [ "groot = groot.__main__:main" ] }
       )
