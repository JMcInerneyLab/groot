from typing import List, cast

from groot.constants import EFormat
from groot.data import global_view
from groot.extensions import ext_files, ext_generating, ext_gimmicks, ext_viewing, ext_modifications
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD
from intermake.engine.environment import MENV
from intermake.engine.plugin import Plugin
from intermake.engine.theme import Theme
from mhelper import string_helper


class Walkthrough:
    """
    SERIALISABLE
    
    Manages the guided wizard.
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
                  pause_splits: bool,
                  pause_consensus: bool,
                  pause_subset: bool,
                  pause_minigraph: bool,
                  pause_sew: bool,
                  pause_clean: bool,
                  pause_check: bool,
                  tolerance: int,
                  alignment: str,
                  tree: str,
                  view: bool,
                  save: bool,
                  outgroups: List[str] ):
        """
        CONSTRUCTOR.
        
        See :function:`ext_gimmicks.wizard` for parameter descriptions. 
        """
        self.new = new
        self.name = name
        self.imports = imports
        self.pause_import = pause_import
        self.pause_components = pause_components
        self.pause_align = pause_align
        self.pause_tree = pause_tree
        self.pause_fusion = pause_fusion
        self.pause_splits = pause_splits
        self.pause_consensus = pause_consensus
        self.pause_subsets = pause_subset
        self.pause_minigraph = pause_minigraph
        self.pause_sew = pause_sew
        self.pause_clean = pause_clean
        self.pause_check = pause_check
        self.tolerance = tolerance
        self.alignment = alignment
        self.tree = tree
        self.view = view
        self.save = save
        self.__stage = 0
        self.is_paused = True
        self.is_completed = False
        self.__result = EChanges.NONE
        self.pause_reason = "start"
        self.outgroups = outgroups
    
    
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
        r.append( "pause_splits      = {}".format( self.pause_splits ) )
        r.append( "pause_consensus   = {}".format( self.pause_consensus ) )
        r.append( "pause_subsets     = {}".format( self.pause_subsets ) )
        r.append( "pause_minigraph   = {}".format( self.pause_minigraph ) )
        r.append( "pause_sew         = {}".format( self.pause_sew ) )
        r.append( "pause_clean       = {}".format( self.pause_clean ) )
        r.append( "pause_check       = {}".format( self.pause_check ) )
        r.append( "tolerance         = {}".format( self.tolerance ) )
        r.append( "alignment         = {}".format( self.alignment ) )
        r.append( "tree              = {}".format( self.tree ) )
        r.append( "view              = {}".format( self.view ) )
        r.append( "stage             = {}".format( self.__stage ) )
        r.append( "is.paused         = {}".format( self.is_paused ) )
        r.append( "is.completed      = {}".format( self.is_completed ) )
        r.append( "last.result       = {}".format( self.__result ) )
        r.append( "pause_reason      = {}".format( self.pause_reason ) )
        r.append( "outgroups         = {}".format( self.outgroups ) )
        
        return "\n".join( r )
    
    
    def __pause( self, title: str, commands: tuple ) -> None:
        self.pause_reason = title
        MCMD.progress( "Walkthrough has paused after {}{}{} due to user request.".format( Theme.BOLD, title, Theme.RESET ) )
        MCMD.progress( "Use the following commands to review:" )
        for command in commands:
            MCMD.progress( "* {}{}{}".format( Theme.COMMAND_NAME,
                                              cast( Plugin, command ).display_name,
                                              Theme.RESET ) )
        MCMD.progress( "Use the {}{}{} command to continue the wizard.".format( Theme.COMMAND_NAME,
                                                                                cast( Plugin, ext_gimmicks.continue_wizard ).display_name,
                                                                                Theme.RESET ) )
        self.is_paused = True
    
    
    def __line( self, title ):
        title = "WIZARD: " + title
        title = " ".join( title.upper() )
        MCMD.progress( Theme.C.SHADE * MENV.host.console_width )
        MCMD.progress( string_helper.centre_align( " " + title + " ", MENV.host.console_width, Theme.C.SHADE ) )
        MCMD.progress( Theme.C.SHADE * MENV.host.console_width )
    
    
    def get_stage_name( self ):
        return self.__stages[self.__stage].__name__
    
    
    def stop( self ):
        Walkthrough.__active_walkthrough = None
        MCMD.progress( "The active wizard has been deleted." )
    
    
    def step( self ) -> EChanges:
        if self.is_completed:
            raise ValueError( "The wizard has already completed." )
        
        self.is_paused = False
        self.__result = EChanges.NONE
        
        while not self.is_paused and self.__stage < len( self.__stages ):
            self.__stages[self.__stage]( self )
            self.__stage += 1
        
        if self.__stage == len( self.__stages ):
            MCMD.progress( "The wizard is complete." )
            self.is_completed = True
        
        return self.__result
    
    
    def __fn8_make_splits( self ):
        self.__line( "Splits" )
        ext_generating.create_splits()
        
        if self.pause_splits:
            self.__pause( "Splits generated", (ext_viewing.print_viable,) )
    
    
    def __fn9_make_consensus( self ):
        self.__line( "Consensus" )
        ext_generating.create_consensus()
        
        if self.pause_consensus:
            self.__pause( "Consensus generated", (ext_viewing.print_candidates,) )
    
    
    def __fn10_make_subsets( self ):
        self.__line( "Subsets" )
        ext_generating.create_subsets()
        
        if self.pause_subsets:
            self.__pause( "Subsets generated", (ext_viewing.print_subsets,) )
    
    
    def __fn11_make_subgraphs( self ):
        self.__line( "Subgraphs" )
        ext_generating.create_subgraphs()
        
        if self.pause_minigraph:
            self.__pause( "Subgraphs generated", (ext_viewing.print_minigraphs,) )
    
    
    def __fn12_make_sewed( self ):
        self.__line( "Raw NRFG" )
        ext_generating.create_fused()
        
        if self.pause_sew:
            self.__pause( "Raw NRFG generated", (ext_viewing.print_trees,) )
    
    
    def __fn13_make_clean( self ):
        self.__line( "Clean NRFG" )
        ext_generating.create_cleaned()
        
        if self.pause_clean:
            self.__pause( "Cleaned NRFG", (ext_viewing.print_trees,) )
    
    
    def __fn14_make_checks( self ):
        self.__line( "Check NRFG" )
        ext_generating.create_checked()
        
        if self.pause_check:
            self.__pause( "Checked NRFG", (ext_viewing.print_trees,) )
    
    
    def __fn15_view_nrfg( self ):
        if self.view:
            self.__result |= ext_viewing.print_trees( graph = global_view.current_model().nrfg.fusion_graph.graph,
                                                      format = EFormat.VISJS,
                                                      file = "open" )
    
    
    def __fn7_make_fusions( self ):
        # Make fusions
        self.__line( "Fusions" )
        self.__result |= ext_generating.create_fusions()
        
        if self.pause_fusion:
            self.__pause( "Fusions identified", (ext_viewing.print_trees, ext_viewing.print_fusions) )
    
    
    def __fn6_make_trees( self ):
        self.__line( "Trees" )
        
        self.__result |= ext_modifications.set_outgroups( self.outgroups )
        
        self.__result |= ext_generating.create_trees( self.tree )
        
        if self.pause_tree:
            self.__pause( "Trees generated", (ext_viewing.print_trees,) )
    
    
    def __fn5_make_alignments( self ):
        self.__line( "Alignments" )
        self.__result |= ext_generating.create_alignments( self.alignment )
        
        if self.pause_align:
            self.__pause( "Domains aligned", (ext_viewing.print_alignments,) )
    
    
    def __fn4_make_components( self ):
        self.__line( "Components" )
        self.__result |= ext_generating.create_components( self.tolerance )
        
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
        MCMD.progress( "The wizard has been activated and is paused. Use the {}{}{} function to begin.".format( Theme.COMMAND_NAME, ext_gimmicks.continue_wizard, Theme.RESET ) )
    
    
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
                __fn8_make_splits,
                __fn9_make_consensus,
                __fn10_make_subsets,
                __fn11_make_subgraphs,
                __fn12_make_sewed,
                __fn13_make_clean,
                __fn14_make_checks,
                __fn15_view_nrfg]
