from typing import List, cast
from mhelper import string_helper
from intermake import MCMD, MENV, Plugin, Theme

import groot.extensions.ext_importation
from groot.constants import EFormat, STAGES, LegoStage
from groot.data import global_view
from groot.extensions import ext_files, ext_generating, ext_gimmicks, ext_viewing, ext_modifications
from groot.frontends.gui.gui_view_utils import EChanges


class Wizard:
    """
    SERIALISABLE
    
    Manages the guided wizard.
    """
    __active_walkthrough: "Wizard" = None
    
    
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
                  pause_pregraphs: bool,
                  pause_minigraph: bool,
                  pause_sew: bool,
                  pause_clean: bool,
                  pause_check: bool,
                  tolerance: int,
                  alignment: str,
                  tree: str,
                  view: bool,
                  save: bool,
                  outgroups: List[str],
                  supertree: str ):
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
        self.pause_pregraphs = pause_pregraphs
        self.pause_sew = pause_sew
        self.pause_clean = pause_clean
        self.pause_check = pause_check
        self.tolerance = tolerance
        self.alignment = alignment
        self.tree = tree
        self.view = view
        self.save = save
        self.supertree = supertree
        self.__stage = 0
        self.is_paused = True
        self.is_completed = False
        self.__result = EChanges.NONE
        self.pause_reason = "start"
        self.outgroups = outgroups
        
        if self.save and not self.name:
            raise ValueError( "Wizard parameter `save` specified but `name` is not set." )
    
    
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
        r.append( "save              = {}".format( self.save ) )
        r.append( "supertree         = {}".format( self.supertree ) )
        
        return "\n".join( r )
    
    
    def __pause( self, title: LegoStage, commands: tuple ) -> None:
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
    
    
    def __line( self, title: object ):
        title = "WIZARD: " + str( title )
        title = " ".join( title.upper() )
        # MCMD.progress( Theme.C.SHADE * MENV.host.console_width )
        MCMD.progress( string_helper.centre_align( " " + title + " ", MENV.host.console_width, Theme.C.SHADE ) )
        # MCMD.progress( Theme.C.SHADE * MENV.host.console_width )
    
    
    def get_stage_name( self ):
        return self.__stages[self.__stage].__name__
    
    
    def stop( self ):
        Wizard.__active_walkthrough = None
        MCMD.progress( "The active wizard has been deleted." )
    
    
    def step( self ) -> EChanges:
        if self.is_completed:
            raise ValueError( "The wizard has already completed." )
        
        self.is_paused = False
        self.__result = EChanges.NONE
        
        while not self.is_paused and self.__stage < len( self.__stages ):
            self.__stages[self.__stage]( self )
            self.__stage += 1
            self.__save_model()
        
        if self.__stage == len( self.__stages ):
            MCMD.progress( "The wizard is complete." )
            self.is_completed = True
        
        return self.__result
    
    
    def __fn8_make_splits( self ):
        self.__line( STAGES.SPLITS_8 )
        ext_generating.create_splits()
        
        if self.pause_splits:
            self.__pause( STAGES.SPLITS_8, (ext_viewing.print_splits,) )
    
    
    def __fn9_make_consensus( self ):
        self.__line( STAGES.CONSENSUS_9 )
        ext_generating.create_consensus()
        
        if self.pause_consensus:
            self.__pause( STAGES.CONSENSUS_9, (ext_viewing.print_consensus,) )
    
    
    def __fn10_make_subsets( self ):
        self.__line( STAGES.SUBSETS_10 )
        ext_generating.create_subsets()
        
        if self.pause_subsets:
            self.__pause( STAGES.SUBSETS_10, (ext_viewing.print_subsets,) )
    
    
    def __fn12_make_subgraphs( self ):
        self.__line( "Subgraphs" )
        ext_generating.create_subgraphs( self.supertree )
        
        if self.pause_minigraph:
            self.__pause( STAGES.SUBGRAPHS_11, (ext_viewing.print_subgraphs,) )
    
    
    def __fn11_make_pregraphs( self ):
        self.__line( "Pregraphs" )
        ext_generating.create_pregraphs()
        
        if self.pause_pregraphs:
            self.__pause( STAGES.PREGRAPHS_11, (ext_viewing.print_pregraphs,) )
    
    
    def __fn13_make_fused( self ):
        self.__line( STAGES.FUSED_12 )
        ext_generating.create_fused()
        
        if self.pause_sew:
            self.__pause( STAGES.FUSED_12, (ext_viewing.print_trees,) )
    
    
    def __fn14_make_clean( self ):
        self.__line( STAGES.CLEANED_13 )
        ext_generating.create_cleaned()
        
        if self.pause_clean:
            self.__pause( STAGES.CLEANED_13, (ext_viewing.print_trees,) )
    
    
    def __fn15_make_checks( self ):
        self.__line( STAGES.CHECKED_14 )
        ext_generating.create_checked()
        
        if self.pause_check:
            self.__pause( STAGES.CHECKED_14, (ext_viewing.print_trees,) )
    
    
    def __fn16_view_nrfg( self ):
        if self.view:
            self.__result |= ext_viewing.print_trees( graph = global_view.current_model().fusion_graph_clean.graph,
                                                      format = EFormat.VISJS,
                                                      file = "open" )
    
    
    def __fn7_make_fusions( self ):
        # Make fusions
        self.__line( STAGES.FUSIONS_7 )
        self.__result |= ext_generating.create_fusions()
        
        if self.pause_fusion:
            self.__pause( STAGES.FUSIONS_7, (ext_viewing.print_trees, ext_viewing.print_fusions) )
    
    
    def __fn6_make_trees( self ):
        self.__line( STAGES.TREES_6 )
        
        self.__result |= ext_modifications.set_outgroups( self.outgroups )
        
        self.__result |= ext_generating.create_trees( self.tree )
        
        if self.pause_tree:
            self.__pause( STAGES.TREES_6, (ext_viewing.print_trees,) )
    
    
    def __fn5_make_alignments( self ):
        self.__line( STAGES.ALIGNMENTS_5 )
        self.__result |= ext_generating.create_alignments( self.alignment )
        
        if self.pause_align:
            self.__pause( STAGES.ALIGNMENTS_5, (ext_viewing.print_alignments,) )
    
    
    def __fn4_make_major( self ):
        self.__line( STAGES.MAJOR_3 )
        self.__result |= ext_generating.create_major( self.tolerance )
        
        if self.pause_components:
            self.__pause( STAGES.MAJOR_3, (ext_viewing.print_genes, ext_viewing.print_components) )
            
    def __fn4_make_minor( self ):
        self.__line( STAGES.MINOR_3 )
        self.__result |= ext_generating.create_minor( self.tolerance )
        
        if self.pause_components:
            self.__pause( STAGES.MINOR_3, (ext_viewing.print_genes, ext_viewing.print_components) )
    
    
    def __fn4b_make_domains( self ):
        self.__line( STAGES.DOMAINS_4 )
        self.__result |= ext_generating.create_domains( "component" )
    
    
    def __fn3_import_data( self ):
        self.__line( STAGES._DATA_0 )
        for import_ in self.imports:
            self.__result |= groot.extensions.ext_importation.import_file( import_ )
        
        if self.pause_import:
            self.__pause( STAGES._DATA_0, (ext_viewing.print_genes,) )
    
    
    def __save_model( self ):
        if self.save:
            self.__line( STAGES._FILE_0 )
            self.__result |= ext_files.file_save( self.name )
    
    
    def __fn1_new_model( self ):
        # Start a new model
        self.__line( "New" )
        if self.new:
            self.__result |= ext_files.file_new()
    
    
    def make_active( self ) -> None:
        Wizard.__active_walkthrough = self
        MCMD.progress( str( self ) )
        MCMD.progress( "The wizard has been activated and is paused. Use the {}{}{} function to begin.".format( Theme.COMMAND_NAME, ext_gimmicks.continue_wizard, Theme.RESET ) )
    
    
    @staticmethod
    def get_active() -> "Wizard":
        return Wizard.__active_walkthrough
    
    
    __stages = [__fn1_new_model,
                __fn3_import_data,
                __fn4_make_major,
                __fn4_make_minor,
                __fn4b_make_domains,
                __fn5_make_alignments,
                __fn6_make_trees,
                __fn7_make_fusions,
                __fn8_make_splits,
                __fn9_make_consensus,
                __fn10_make_subsets,
                __fn11_make_pregraphs,
                __fn12_make_subgraphs,
                __fn13_make_fused,
                __fn14_make_clean,
                __fn15_make_checks,
                __fn16_view_nrfg]
