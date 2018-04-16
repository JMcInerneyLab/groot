from distutils.core import setup


setup( name = "groot",
       url = "https://bitbucket.org/mjr129/groot",
       version = "0.0.0.45",
       description = "Generate N-rooted fusion graphs from genomic data.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["groot",
                   "groot_ex",
                   "groot.algorithms",
                   "groot.data",
                   "groot.extensions",
                   "groot.frontends",
                   "groot.frontends.gui",
                   "groot.frontends.gui.forms",
                   "groot.frontends.gui.forms.designer",
                   "groot.frontends.gui.forms.resources",
                   "groot.utilities",
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
                           "biopython",
                           "six",  # groot doesn't use this, but ete needs it
                           ],
       python_requires = ">=3.6"
       )
