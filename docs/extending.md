Extending Groot
===============

Creating extension modules
--------------------------

You can incorporate your own extensions into Groot.

Algorithms should be written into a Python package or module.

Inside your modules, register Groot algorithms using the `@xyz.register` decorators:
```python
from groot import tree_algorithms

@tree_algorithms.register()
def my_algorithm( . . . )
    . . .
```

The `groot_ex` package contains the default set of algorithms, you can use this as a template for your own.

New Groot commands can also be registered using Intermake.
```python
from intermake import command

@command()
def my_command( . . . ):
    . . .
```

The groot core commands can be found in the main `groot` package, inside the `extensions` subfolder.
See the Intermake documentation for more details.

### Registering the modules ###

Once created, you need to register your package with Groot.
From the BASH command line:

```
groot import my_algorithms +persist
```

This says:
* Start `groot`, `import` the module `my_algorithms` and `+persist` this setting for the next time I start Groot.


Modifying the source code
-------------------------

The Gʀᴏᴏᴛ source code is fully documented inline.

It is arranged into a simple MVC-like architecture:

* The model:
    * The dynamic model (`data`):
        * Sequences
        * Subsequences
        * Edges
        * Components
        * etc. 
    * The static model (`algorithms/`):
        * Tree algorithms
        * Alignment algorithms
        * Supertree algorithms
        * etc. 
* The controller (`extensions`)
* The view:
    * CLI (Iɴᴛᴇʀᴍᴀᴋᴇ library)
    * GUI (`frontends/gui`)
    
