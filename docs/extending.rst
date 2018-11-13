================================================================================
                                Extending Groot                                 
================================================================================

This tutorial shows you how to incorporate your own extensions into Groot.

.. note::

    * *Algorithms* control how Groot performs a *particular operation*
        * The ``groot_ex`` package contains the default set of *algorithms*.
    * *Commands* control what *operations are available*
        * The ``groot.commands`` package contains the default set of *commands*
     
    You can use the code from these packages as templates for your own extensions!

.. _`Creating algorithms`:

--------------------------------------------------------------------------------
                              Creating algorithms                               
--------------------------------------------------------------------------------

Algorithms form the collection of options the user has when, for instance,
calculating the similarity matrix. For instance the following command::

    groot create_similarities blastp
    
Specifies use of the ``blastp`` algorithm to create the similarity matrix.
    
Your own algorithms should be written into a Python package.

For this tutorial, we'll add the complementary ``blastn`` algorithm to Groot.

Start by creating the basic package structure::

    mkdir my_extension
    cd my_extension
    mkdir my_extension

Now create your package script ``__init__.py`` using your favourite editor, :t:`vim`::

    vim __init__.py

Add the following to the file::

    import groot
    import mhelper
    
    @groot.similarity_algorithms.register( "blastn" )
    def blastp( fasta: str ) -> str:
        file_helper.write_all_text( "fasta.fasta", fasta )
        groot.subprocess_helper.execute( ["blastn", "-query", "fasta.fasta", "-subject", "fasta.fasta", "-outfmt", "6", "-out", "blast.blast"] )
        return file_helper.read_all_text( "blast.blast" )

Exit :t:`vim`, remembering to save your file.
Navigate back to the main folder and create the ``setup.py`` for your package::

    cd ..
    vim setup.py

Specify the following::

    from distutils.core import setup

    setup( name = "my_extension",
           packages = ["my_extension"],
           python_requires = ">=3.6",
           install_requires = ["groot", "mhelper"]
           )
           
Exit :t:`vim`. Your package's directory structure should now look like this::

    ...
     |
     |- my_extension
        |- my_extension
        |   |- __init__.py
        |- setup.py

Install your package using ``pip``::

    sudo pip install -e .
    
Import your package into Groot::

    groot import my_extension +persist
    
That's it! You should be able to see your new algorithm in Groot::

    groot help algorithms
    
And use it::

    groot create_similarities blastn


--------------------------------------------------------------------------------
                               Creating commands                                
--------------------------------------------------------------------------------

Commands can also be added to Groot's CLI.

For this tutorial we'll add a command that shows the current filename.

Follow the same process as for `Creating algorithms`_ above, but replace your ``__init__.py`` with this::

    import intermake
    import groot
    
    @intermake.command()
    def print_file_name():
        print( groot.current_model().file_name )

After registering with Groot you can use your command like so::

    groot print_file_name


--------------------------------------------------------------------------------
                           Modifying the source code                            
--------------------------------------------------------------------------------

The Groot source code is fully documented and annotated for use with help and autocomplete in your favourite IDE.

The main Groot logic is contained in `groot.commands` and Groot's data classes
are contained in `groot.data`. Groot's entry point can be found in ``__main__.py``.

