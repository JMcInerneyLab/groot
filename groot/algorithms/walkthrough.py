from typing import List, cast

from groot.constants import EFormat
from groot.data import global_view
from groot.extensions import ext_files, ext_generating, ext_gimmicks, ext_viewing
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD
from intermake.engine.environment import MENV
from intermake.engine.plugin import Plugin
from intermake.engine.theme import Theme
from mhelper import string_helper


class Walkthrough:
    """
    SERIALISABLE
    
    Manages the guided walkthrough.
    """
    __active_walkthrough: "Walkthrough" = None
    
    
    def __init__( self,
                  new: bool,
                  name: str,
                  imports: List[str],
                  pause_import: bool,
                  pause_components: bool,
                  pause_align: bool,
                  pause_tree: bool,
                  pause_fusion: bool,
                  pause_nrfg: bool,
                  tolerance: int,
                  alignment: str,
                  tree: str,
                  view: bool ):
        """
        CONSTRUCTOR.
        
        See :function:`ext_gimmicks.walkthrough` for parameter descriptions. 
        """
        self.new = new
        self.name = name
        self.imports = imports
        self.pause_import = pause_import
        self.pause_components = pause_components
        self.pause_align = pause_align
        self.pause_tree = pause_tree
        self.pause_fusion = pause_fusion
        self.pause_nrfg = pause_nrfg
        self.tolerance = tolerance
        self.alignment = alignment
        self.tree = tree
        self.view = view
        self.__stage = 0
        self.is_paused = True
        self.is_completed = False
        self.__result = EChanges.NONE
        self.pause_reason = "start"
    
    
    def __str__( self ):
        r = []
        r.append( "new               = {}".format( self.new ) )
        r.append( "name              = {}".format( self.name ) )
        r.append( "imports           = {}".format( self.imports ) )
        r.append( "pause_import      = {}".format( self.pause_import ) )
        r.append( "pause_components  = {}".format( self.pause_components ) )
        r.append( "pause_align       = {}".format( self.pause_align ) )
        r.append( "pause_tree        = {}".format( self.pause_tree ) )
        r.append( "pause_fusion      = {}".format( self.pause_fusion ) )
        r.append( "pause_nrfg        = {}".format( self.pause_nrfg ) )
        r.append( "tolerance         = {}".format( self.tolerance ) )
        r.append( "alignment         = {}".format( self.alignment ) )
        r.append( "tree              = {}".format( self.tree ) )
        r.append( "view              = {}".format( self.view ) )
        r.append( "stage             = {}".format( self.__stage ) )
        r.append( "is.paused         = {}".format( self.is_paused ) )
        r.append( "is.completed      = {}".format( self.is_completed ) )
        r.append( "last.result       = {}".format( self.__result ) )
        r.append( "pause_reason      = {}".format( self.pause_reason ) )
        
        return "\n".join( r )
    
    
    def __pause( self, title: str, commands: tuple ) -> None:
        self.pause_reason = title
        MCMD.progress( "Walkthrough has paused after {}{}{} due to user request.".format( Theme.BOLD, title, Theme.RESET ) )
        MCMD.progress( "Use the following commands to review:" )
        for command in commands:
            MCMD.progress( "* {}{}{}".format( Theme.COMMAND_NAME,
                                              cast( Plugin, command ).display_name,
                                              Theme.RESET ) )
        MCMD.progress( "Use the {}{}{} command to continue the walkthrough.".format( Theme.COMMAND_NAME,
                                                                                     cast( Plugin, ext_gimmicks.continue_walkthrough ).display_name,
                                                                                     Theme.RESET ) )
        self.is_paused = True
    
    
    def __line( self, title ):
        title = "WIZARD: " + title
        title = " ".join( title.upper() )
        MCMD.progress( Theme.C.SHADE * MENV.host.console_width )
        MCMD.progress( string_helper.centre_align( " " + title + " ", MENV.host.console_width, Theme.C.SHADE ) )
        MCMD.progress( Theme.C.SHADE * MENV.host.console_width )
    
    
    def step( self ) -> EChanges:
        if self.is_completed:
            raise ValueError( "The walkthrough has already completed." )
        
        self.is_paused = False
        self.__result = EChanges.NONE
        
        while not self.is_paused and self.__stage < len( self.__stages ):
            self.__stages[self.__stage]( self )
            self.__stage += 1
        
        if self.__stage == len( self.__stages ):
            MCMD.progress( "The walkthrough is complete." )
            self.is_completed = True
        
        return self.__result
    
    
    def __fn9_view_nrfg( self ):
        if self.view:
            self.__result |= ext_viewing.print_trees( graph = global_view.current_model().nrfg.graph, format = EFormat.VISJS, file = "open" )
    
    
    def __fn8_make_nrfg( self ):
        self.__line( "NRFG" )
        ext_generating.make_nrfg()
        
        if self.pause_nrfg:
            self.__pause( "NRFG generated", (ext_viewing.print_trees,) )
    
    
    def __fn7_make_fusions( self ):
        # Make fusions
        self.__line( "Fusions" )
        self.__result |= ext_generating.make_fusions()
        
        if self.pause_fusion:
            self.__pause( "Fusions identified", (ext_viewing.print_trees, ext_viewing.print_fusions) )
    
    
    def __fn6_make_trees( self ):
        self.__line( "Trees" )
        
        self.__result |= ext_generating.make_trees( self.tree )
        
        if self.pause_tree:
            self.__pause( "Trees generated", (ext_viewing.print_trees,) )
    
    
    def __fn5_make_alignments( self ):
        self.__line( "Alignments" )
        self.__result |= ext_generating.make_alignments( self.alignment )
        
        if self.pause_align:
            self.__pause( "Domains aligned", (ext_viewing.print_alignments,) )
    
    
    def __fn4_make_components( self ):
        self.__line( "Components" )
        self.__result |= ext_generating.make_components( self.tolerance )
        
        if self.pause_components:
            self.__pause( "components generated", (ext_viewing.print_genes, ext_viewing.print_components) )
    
    
    def __fn3_import_data( self ):
        self.__line( "Import" )
        for import_ in self.imports:
            self.__result |= ext_files.import_file( import_ )
        
        if self.pause_import:
            self.__pause( "data imported", (ext_viewing.print_genes,) )
    
    
    def __fn2_save_model( self ):
        self.__line( "Save" )
        if not global_view.current_model().file_name:
            self.__result |= ext_files.file_save( self.name )
        elif self.name is not None:
            raise ValueError( "`name` parameter specified but the model is already named." )
    
    
    def __fn1_new_model( self ):
        # Start a new model
        self.__line( "Clean" )
        if self.new:
            self.__result |= ext_files.file_new()
    
    
    def make_active( self ) -> None:
        Walkthrough.__active_walkthrough = self
        MCMD.progress( str( self ) )
        MCMD.progress( "The walkthrough has been activated and is paused. Use the {}{}{} function to begin.".format( Theme.COMMAND_NAME, ext_gimmicks.continue_walkthrough, Theme.RESET ) )
    
    
    @staticmethod
    def get_active() -> "Walkthrough":
        return Walkthrough.__active_walkthrough
    
    
    __stages = [__fn1_new_model,
                __fn2_save_model,
                __fn3_import_data,
                __fn4_make_components,
                __fn5_make_alignments,
                __fn6_make_trees,
                __fn7_make_fusions,
                __fn8_make_nrfg,
                __fn9_view_nrfg]
