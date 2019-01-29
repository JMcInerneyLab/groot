from distutils.core import setup


setup( name = "groot",
       url = "https://bitbucket.org/mjr129/groot",
       version = "0.0.0.61",
       description = "Generate N-rooted fusion graphs from genomic data.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["groot",
                   "groot.application",
                   "groot.commands",
                   "groot.commands.gimmicks",
                   "groot.commands.workflow",
                   "groot.data",
                   "groot.utilities",
                   "groot_ex",
                   "groot_gui",
                   "groot_gui.lego",
                   "groot_gui.forms",
                   "groot_gui.forms.designer",
                   "groot_gui.forms.resources",
                   "groot_gui.utilities",
                   "groot_tests"
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
                           "editorium",
                           "six",  # groot doesn't use this, but ete needs it
                           ],
       python_requires = ">=3.6",

       classifiers = \
           [
               "Development Status :: 3 - Alpha",
        
               "Environment :: Console",
               "Environment :: Win32 (MS Windows)",
               "Environment :: X11 Applications :: Qt",
               "Environment :: MacOS X",
               "Operating System :: OS Independent",
               "Operating System :: Microsoft :: Windows",
               "Operating System :: MacOS",
               "Operating System :: POSIX :: Linux",
        
               "Intended Audience :: Science/Research",
               "Topic :: Scientific/Engineering",
               "Topic :: Scientific/Engineering :: Bio-Informatics",
               "Topic :: Utilities",
               "Topic :: Terminals",
               "Topic :: Multimedia :: Graphics :: Editors",
               "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
               "Topic :: Multimedia :: Graphics :: Presentation",
               "Topic :: Multimedia :: Graphics :: Viewers",
        
        
               "License :: OSI Approved :: GNU Affero General Public License v3",
               "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        
               "Natural Language :: English",
               "Programming Language :: Python :: 3.6",
               "Programming Language :: Python :: 3",
               "Programming Language :: Python :: 3 :: Only",
               "Programming Language :: Other Scripting Engines"
           ]
       )
