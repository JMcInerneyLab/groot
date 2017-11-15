from distutils.core import setup


setup( name = "groot",
       url="https://bitbucket.org/mjr129/groot",
       version = "0.0.0.8",
       description = "Generate N-rooted fusion graphs from genomic data.",
       author = "Martin Rusilowicz",
       license = "GPLv3",
       packages = [ "groot",
                    "groot.algorithms",
                    "groot.data",
                    "groot.extensions",
                    "groot.frontends",
                    "groot.frontends.cli",
                    "groot.frontends.gui",
                    "groot.frontends.gui.forms",
                    "groot.frontends.gui.forms.designer",
                    ],
       entry_points= { "console_scripts": [ "groot = groot.__main__:main" ] },
       install_requires = ["ete3"]
       )
