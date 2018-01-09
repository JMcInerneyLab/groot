import os
import shutil
from typing import Sequence, Optional

import re

from groot.algorithms import external_tools
from intermake.engine import constants
from intermake.engine.constants import EStream
from intermake.engine.environment import MCMD, MENV
from mhelper import file_helper, async_helper, SubprocessError


class __SubprocessRun:
    def __init__( self, garbage ):
        self.garbage = garbage
        self.nx1 = [True, True]
    
    
    def __print( self, x, s, i ):
        if any( y.search( x ) for y in self.garbage ):
            return
        
        if not x:
            if self.nx1[i]:
                return
            
            self.nx1[i] = True
        else:
            self.nx1[i] = False
        
        MCMD.print( x, stream = s )
    
    
    def print_1( self, x ):
        self.__print( x, EStream.EXTERNAL_STDOUT, 0 )
    
    
    def print_2( self, x ):
        self.__print( x, EStream.EXTERNAL_STDERR, 1 )


def run_subprocess( command: Sequence[str], garbage = None ):
    """
    Runs the specified subprocess
    
    :param command: Commands and arguments
    :param garbage: List containing one or more regex that specify lines dropped from display 
    """
    if garbage is None:
        garbage = []
    
    garbage = [re.compile( x ) for x in garbage]
    
    spr = __SubprocessRun( garbage )
    
    try:
        async_helper.async_run( command, spr.print_1, spr.print_2, check = True )
    except SubprocessError as ex:
        MCMD.question( "Halting to inspect subprocess error", [None], None )


def run_in_temporary( function, *args, **kwargs ):
    """
    Sets the working directory to a temporary folder inside the current working directory.
    Calls `function`
    Then deletes the temporary folder and returns to the original working directory. 
    """
    temp_folder_name = os.path.join( MENV.local_data.local_folder( constants.FOLDER_TEMPORARY ), "generate-tree" )
    
    if os.path.exists( temp_folder_name ):
        shutil.rmtree( temp_folder_name )
    
    file_helper.create_directory( temp_folder_name )
    os.chdir( temp_folder_name )
    
    try:
        return function( *args, **kwargs )
    finally:
        os.chdir( ".." )
        shutil.rmtree( temp_folder_name )


def get_tool( prefix, tool: Optional[str] ):
    """
    Gets the specified function from the `external_tools` module.
    """
    if not tool:
        tool = "default"
    
    name = prefix + "_" + tool
    
    try:
        return getattr( external_tools, name )
    except AttributeError:
        raise ValueError( "No such «{}» algorithm as «{}». (the «{}» function does not exist in the `external_tools` module.)".format( prefix, tool, name ) )
