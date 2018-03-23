from distutils.core import setup


setup( name = "groot",
       url = "https://bitbucket.org/mjr129/groot",
       version = "0.0.0.40",
       description = "Generate N-rooted fusion graphs from genomic data.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       include_package_data = True,
       packages = ["groot",
                   "groot.algorithms",
                   "groot.algorithms.extendable",
                   "groot.data",
                   "groot.extensions",
                   "groot.frontends",
                   "groot.frontends.cli",
                   "groot.frontends.gui",
                   "groot.frontends.gui.forms",
                   "groot.frontends.gui.forms.designer",
                   "groot.frontends.gui.forms.resources",
                   ],
       entry_points = { "console_scripts": ["groot = groot.__main__:main"] },
       install_requires = ["intermake",  # MJR, architecture
                           "mhelper",  # MJR, general
                           "pyperclip",  # clipboard
                           "colorama",  # ui (cli)
                           "mgraph",  # MJR
                           "stringcoercion",  # MJR
                           "PyQt5",  # ui (GUI)
                           "sip",  # ui (GUI)
                           "dendropy",
                           "mgvis",  # MJR (bundler)
                           "biopython",
                           "six",  # groot doesn't use this, but ete needs it
                           ],
       python_requires = ">=3.6"
       )
