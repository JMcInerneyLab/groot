from intermake import MCMD, AbstractCommand, Theme, VisualisablePath, command, common_commands, console_explorer, visibilities
from mhelper import EFileMode, Filename, MFlags, file_helper, string_helper
from typing import List, Optional, cast

from groot import Model, constants
from groot.algorithms import workflow
from groot.constants import EFormat, Stage, STAGES, EChanges
from groot.data import global_view


__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME_EXTRA


class EImportFilter( MFlags ):
    """
    Mask on importing files.
    
    :cvar DATA: Data files (`.fasta`, `.blast`, `.composites`)
    :cvar MODEL: Model files (`.groot`)
    :cvar SCRIPT: Scripts (`.imk`)
    """
    DATA: "EImportFilter" = 1 << 0
    MODEL: "EImportFilter" = 1 << 1
    SCRIPT: "EImportFilter" = 1 << 2


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
    
    
    def __pause( self, title: Stage, commands: tuple ) -> None:
        self.pause_reason = title
        MCMD.progress( "Walkthrough has paused after {}{}{} due to user request.".format( Theme.BOLD, title, Theme.RESET ) )
        MCMD.progress( "Use the following commands to review:" )
        for command in commands:
            MCMD.progress( "* {}{}{}".format( Theme.COMMAND_NAME,
                                              cast( AbstractCommand, command ).display_name,
                                              Theme.RESET ) )
        MCMD.progress( "Use the {}{}{} command to continue the wizard.".format( Theme.COMMAND_NAME,
                                                                                cast( AbstractCommand, continue_wizard ).display_name,
                                                                                Theme.RESET ) )
        self.is_paused = True
    
    
    def __line( self, title: object ):
        title = "WIZARD: " + str( title )
        title = " ".join( title.upper() )
        # MCMD.progress( Theme.C.SHADE * MENV.host.console_width )
        MCMD.progress( string_helper.centre_align( " " + title + " ", MCMD.host.console_width, Theme.C.SHADE ) )
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
        workflow.s100_splits.create_splits()
        
        if self.pause_splits:
            self.__pause( STAGES.SPLITS_8, (workflow.s100_splits.print_splits,) )
    
    
    def __fn9_make_consensus( self ):
        self.__line( STAGES.CONSENSUS_9 )
        workflow.s110_consensus.create_consensus()
        
        if self.pause_consensus:
            self.__pause( STAGES.CONSENSUS_9, (workflow.s110_consensus.print_consensus,) )
    
    
    def __fn10_make_subsets( self ):
        self.__line( STAGES.SUBSETS_10 )
        workflow.s120_subsets.create_subsets()
        
        if self.pause_subsets:
            self.__pause( STAGES.SUBSETS_10, (workflow.s120_subsets.print_subsets,) )
    
    
    def __fn12_make_subgraphs( self ):
        self.__line( "Subgraphs" )
        workflow.s140_supertrees.create_supertrees( self.supertree )
        
        if self.pause_minigraph:
            self.__pause( STAGES.SUBGRAPHS_11, (workflow.s140_supertrees.print_supertrees,) )
    
    
    def __fn11_make_pregraphs( self ):
        self.__line( "Pregraphs" )
        workflow.s130_pregraphs.create_pregraphs()
        
        if self.pause_pregraphs:
            self.__pause( STAGES.PREGRAPHS_11, (workflow.s130_pregraphs.print_pregraphs,) )
    
    
    def __fn13_make_fused( self ):
        self.__line( STAGES.FUSED_12 )
        workflow.s150_fuse.create_fused()
        
        if self.pause_sew:
            self.__pause( STAGES.FUSED_12, (workflow.s080_tree.print_trees,) )
    
    
    def __fn14_make_clean( self ):
        self.__line( STAGES.CLEANED_13 )
        workflow.s160_clean.create_cleaned()
        
        if self.pause_clean:
            self.__pause( STAGES.CLEANED_13, (workflow.s080_tree.print_trees,) )
    
    
    def __fn15_make_checks( self ):
        self.__line( STAGES.CHECKED_14 )
        workflow.s170_checked.create_checked()
        
        if self.pause_check:
            self.__pause( STAGES.CHECKED_14, (workflow.s080_tree,) )
    
    
    def __fn16_view_nrfg( self ):
        if self.view:
            self.__result |= workflow.s080_tree.print_trees( graph = global_view.current_model().fusion_graph_clean.graph,
                                                             format = EFormat.VISJS,
                                                             file = "open" )
    
    
    def __fn7_make_fusions( self ):
        # Make fusions
        self.__line( STAGES.FUSIONS_7 )
        self.__result |= workflow.s090_fusion_events.create_fusions()
        
        if self.pause_fusion:
            self.__pause( STAGES.FUSIONS_7, (workflow.s080_tree.print_trees, workflow.s090_fusion_events.print_fusions) )
    
    
    def __fn6_make_trees( self ):
        self.__line( STAGES.TREES_6 )
        
        model = global_view.current_model()
        ogs = [model.genes[x] for x in self.outgroups]
        
        self.__result |= workflow.s055_outgroups.set_outgroups( ogs )
        
        self.__result |= workflow.s080_tree.create_trees( self.tree )
        
        if self.pause_tree:
            self.__pause( STAGES.TREES_6, (workflow.s080_tree.print_trees,) )
    
    
    def __fn5_make_alignments( self ):
        self.__line( STAGES.ALIGNMENTS_5 )
        self.__result |= workflow.s070_alignment.create_alignments( self.alignment )
        
        if self.pause_align:
            self.__pause( STAGES.ALIGNMENTS_5, (workflow.s070_alignment.print_alignments,) )
    
    
    def __fn4_make_major( self ):
        self.__line( STAGES.MAJOR_3 )
        self.__result |= workflow.s040_major.create_major( self.tolerance )
        
        if self.pause_components:
            self.__pause( STAGES.MAJOR_3, (workflow.s020_sequences.print_genes, workflow.s040_major.print_major) )
    
    
    def __fn4_make_minor( self ):
        self.__line( STAGES.MINOR_3 )
        self.__result |= workflow.s050_minor.create_minor( self.tolerance )
        
        if self.pause_components:
            self.__pause( STAGES.MINOR_3, (workflow.s020_sequences.print_genes, workflow.s050_minor.print_minor) )
    
    
    def __fn4b_make_domains( self ):
        self.__line( STAGES.DOMAINS_4 )
        self.__result |= workflow.s060_userdomains.create_domains( "component" )
    
    
    def __fn3_import_data( self ):
        self.__line( STAGES._DATA_0 )
        for import_ in self.imports:
            self.__result |= import_file( import_ )
        
        if self.pause_import:
            self.__pause( STAGES._DATA_0, (workflow.s020_sequences.print_genes,) )
    
    
    def __save_model( self ):
        if self.save:
            self.__line( STAGES._FILE_0 )
            self.__result |= workflow.s010_file.file_save( self.name )
    
    
    def __fn1_new_model( self ):
        # Start a new model
        self.__line( "New" )
        if self.new:
            self.__result |= workflow.s010_file.file_new()
    
    
    def make_active( self ) -> None:
        Wizard.__active_walkthrough = self
        MCMD.progress( str( self ) )
        MCMD.progress( "The wizard has been activated and is paused. Use the {}{}{} function to begin.".format( Theme.COMMAND_NAME, continue_wizard, Theme.RESET ) )
    
    
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


@command( folder = constants.F_CREATE )
def create_wizard( new: Optional[bool] = None,
                   name: Optional[str] = None,
                   imports: Optional[List[str]] = None,
                   outgroups: Optional[List[str]] = None,
                   tolerance: Optional[int] = None,
                   alignment: Optional[str] = None,
                   supertree: Optional[str] = None,
                   tree: Optional[str] = None,
                   view: Optional[bool] = None,
                   save: Optional[bool] = None,
                   pause_import: Optional[bool] = None,
                   pause_components: Optional[bool] = None,
                   pause_align: Optional[bool] = None,
                   pause_tree: Optional[bool] = None,
                   pause_fusion: Optional[bool] = None,
                   pause_splits: Optional[bool] = None,
                   pause_consensus: Optional[bool] = None,
                   pause_subset: Optional[bool] = None,
                   pause_pregraphs: Optional[bool] = None,
                   pause_minigraph: Optional[bool] = None,
                   pause_sew: Optional[bool] = None,
                   pause_clean: Optional[bool] = None,
                   pause_check: Optional[bool] = None ) -> None:
    """
    Sets up a workflow that you can activate in one go.
    
    If you don't fill out the parameters then whatever UI you are using will prompt you for them.
    
    If you have a set of default parameters that you'd like to preserve, take a look at the `alias` command.
    
    This method is represented in the GUI by the wizard window.
    
    :param pause_pregraphs:     Pause after stage. 
    :param new:                 Create a new model? 
    :param name:                Name the model?
    :param outgroups:           Outgroup accessions?
    :param imports:             Import files into the model? 
    :param tolerance:           Component identification tolerance? 
    :param alignment:           Alignment method?
    :param supertree:           Supertree method? 
    :param tree:                Tree generation method?
    :param view:                View the final NRFG in Vis.js?
    :param save:                Save file to disk? (requires `name`)
    :param pause_components:    Pause after stage. 
    :param pause_import:        Pause after stage. 
    :param pause_align:         Pause after stage. 
    :param pause_tree:          Pause after stage. 
    :param pause_fusion:        Pause after stage. 
    :param pause_splits:        Pause after stage.
    :param pause_consensus:     Pause after stage.
    :param pause_subset:        Pause after stage.
    :param pause_minigraph:     Pause after stage.
    :param pause_sew:           Pause after stage.
    :param pause_clean:         Pause after stage.
    :param pause_check:         Pause after stage.
    """
    if new is None:
        new = (MCMD.question( "1/14. Are you starting a new model, or do you want to continue with your current data?", ["new", "continue"] ) == "new")
    
    if name is None:
        name = MCMD.question( "Name your model.\nYou can specify a complete path or just a name.\nIf you don't enter a name, your won't have the option to save your file using the wizard, though you can still do so manually.", ["*"] )
        
        if not name:
            MCMD.warning( "Your file will not be saved by the wizard." )
    
    if imports is None:
        imports = []
        
        while True:
            ex = "\nEnter a blank line when you don't want to add any more files." if imports else ""
            file_name = MCMD.question( "Enter file paths to import BLAST or FASTA files, one per line." + ex, ["*"] )
            
            if file_name:
                imports.append( file_name )
            else:
                break
    
    if outgroups is None:
        outgroups = []
        
        while True:
            ex = "\nEnter a blank line when you don't want to add any more outgroups."
            outgroup = MCMD.question( "Enter outgroup accessions, one per line." + ex, ["*"] )
            
            if outgroup:
                outgroups.append( outgroup )
            else:
                break
    
    if tolerance is None:
        success = False
        
        while not success:
            tolerance_str = MCMD.question( "What tolerance do you want to use for the component identification?", ["*"] )
            
            try:
                tolerance = int( tolerance_str )
                success = True
            except:
                MCMD.print( "Something went wrong. Let's try that question again." )
                success = False
    
    if alignment is None:
        alignment = question( "Which function do you want to use for the sequence alignment? Enter a blank line for the default.", list( workflow.s070_alignment.alignment_algorithms.keys ) + [""] )
    
    if tree is None:
        tree = question( "Which function do you want to use for the tree generation? Enter a blank line for the default.", list( workflow.s080_tree.tree_algorithms.keys ) + [""] )
    
    if supertree is None:
        supertree = question( "Which function do you want to use for the supertree generation? Enter a blank line for the default.", list( workflow.s140_supertrees.supertree_algorithms.keys ) + [""] )
    
    if pause_import is None:
        pause_import = question( "Do you wish the wizard to pause for you to review the imported data?" )
    
    if pause_components is None:
        pause_components = question( "Do you wish the wizard to pause for you to review the components?" )
    
    if pause_align is None:
        pause_align = question( "Do you wish the wizard to pause for you to review the alignments?" )
    
    if pause_tree is None:
        pause_tree = question( "Do you wish the wizard to pause for you to review the trees?" )
    
    if pause_fusion is None:
        pause_fusion = question( "Do you wish the wizard to pause for you to review the fusions?" )
    
    if pause_splits is None:
        pause_splits = question( "Do you wish the wizard to pause for you to review the candidate splits?" )
    
    if pause_consensus is None:
        pause_consensus = question( "Do you wish the wizard to pause for you to review the consensus splits?" )
    
    if pause_subset is None:
        pause_subset = question( "Do you wish the wizard to pause for you to review the subsets?" )
    
    if pause_pregraphs is None:
        pause_pregraphs = question( "Do you wish the wizard to pause for you to review the pregraphs?" )
    
    if pause_minigraph is None:
        pause_minigraph = question( "Do you wish the wizard to pause for you to review the subgraphs?" )
    
    if pause_sew is None:
        pause_sew = question( "Do you wish the wizard to pause for you to review the uncleaned NRFG?" )
    
    if pause_clean is None:
        pause_clean = question( "Do you wish the wizard to pause for you to review the cleaned NRFG?" )
    
    if pause_check is None:
        pause_check = question( "Do you wish the wizard to pause for you to review the checks?" )
    
    if view is None:
        view = question( "Do you wish the wizard to show you the final NRFG in Vis.js?" )
    
    if save is None:
        if not name:
            save = False
        else:
            save = question( "Save your model after each stage completes?" )
    
    walkthrough = Wizard( new = new,
                          name = name,
                          imports = imports,
                          pause_import = pause_import,
                          pause_components = pause_components,
                          pause_align = pause_align,
                          pause_tree = pause_tree,
                          pause_fusion = pause_fusion,
                          pause_splits = pause_splits,
                          pause_consensus = pause_consensus,
                          pause_subset = pause_subset,
                          pause_pregraphs = pause_pregraphs,
                          pause_minigraph = pause_minigraph,
                          pause_sew = pause_sew,
                          pause_clean = pause_clean,
                          pause_check = pause_check,
                          tolerance = tolerance,
                          alignment = alignment,
                          tree = tree,
                          view = view,
                          save = save,
                          outgroups = outgroups,
                          supertree = supertree )
    
    walkthrough.make_active()
    MCMD.progress( "The wizard has been created paused.\nYou can use the {} and {} commands to manage your wizard.".format( continue_wizard, drop_wizard ) )


@command( visibility = visibilities.ADVANCED, names = ["continue"] )
def continue_wizard() -> EChanges:
    """
    Continues the wizard after it was paused.
    """
    if Wizard.get_active() is None:
        raise ValueError( "There is no active wizard to continue." )
    
    return Wizard.get_active().step()


@command( visibility = visibilities.ADVANCED, names = ["stop"], folder = constants.F_DROP )
def drop_wizard() -> EChanges:
    """
    Stops a wizard.
    """
    if Wizard.get_active() is None:
        raise ValueError( "There is no active wizard to stop." )
    
    Wizard.get_active().stop()
    return EChanges.NONE


def question( *args ):
    return MCMD.question( *args )


@command( folder = constants.F_CREATE )
def create_components( tol: int = 0 ):
    """
    Executes `create_major` then `create_minor`.
    :param tol: Tolerance
    """
    return (workflow.s040_major.create_major( tol ) |
            workflow.s050_minor.create_minor( tol ))


@command( folder = constants.F_DROP )
def drop_components() -> EChanges:
    """
    Removes all the components from the model.
    """
    count = workflow.s040_major.drop_major()
    
    MCMD.progress( "Dropped all {} components from the model.".format( count ) )
    
    return EChanges.COMPONENTS


@command( folder = constants.F_IMPORT )
def import_file( file_name: Filename[EFileMode.READ],
                 skip_bad_extensions: bool = False,
                 filter: EImportFilter = EImportFilter.DATA,
                 query: bool = False ) -> EChanges:
    """
    Imports a file.
    _How_ the file is imported is determined by its extension.

        `.groot`     --> `file_load`
        `.fasta`     --> `import_fasta`
        `.blast`     --> `import_blast`
        `.composite` --> `import_composite`
        `.imk`       --> `source` (runs the script)    
     
    :param file_name:               Name of file to import. 
    :param skip_bad_extensions:     When set, if the file has an extension we don't recognise, no error is raised. 
    :param filter:                  Specifies what kind of files we are allowed to import.
    :param query:                   When set the kind of the file is printed to `MCMD` and the file is not imported. 
    :return:                        Nothing is returned, the file data is incorporated into the model and messages are sent via `MCMD`.
    """
    ext = file_helper.get_extension( file_name ).lower()
    
    if filter.DATA:
        if ext == ".blast":
            if not query:
                return workflow.s030_similarity.import_similarity( file_name )
            else:
                MCMD.print( "BLAST: «{}».".format( file_name ) )
                return EChanges.INFORMATION
        elif ext in (".fasta", ".fa", ".faa"):
            if not query:
                return workflow.s020_sequences.import_genes( file_name )
            else:
                MCMD.print( "FASTA: «{}».".format( file_name ) )
                return EChanges.INFORMATION
    
    if filter.SCRIPT:
        if ext == ".imk":
            if not query:
                MCMD.progress( "Run script «{}».".format( file_name ) )
                common_commands.cmd_source( file_name )
                return EChanges.MODEL_OBJECT
            else:
                MCMD.print( "Script: «{}».".format( file_name ) )
                return EChanges.INFORMATION
    
    if filter.MODEL:
        if ext == ".groot":
            if not query:
                return workflow.s010_file.file_load( file_name )
            else:
                MCMD.print( "Model: «{}».".format( file_name ) )
                return EChanges.INFORMATION
    
    if skip_bad_extensions:
        return EChanges.NONE
    
    raise ValueError( "Cannot import the file '{}' because I don't recognise the extension '{}'.".format( file_name, ext ) )


@command( folder = constants.F_IMPORT )
def import_directory( directory: str, query: bool = False, filter: EImportFilter = (EImportFilter.DATA | EImportFilter.SCRIPT), reset: bool = True ) -> EChanges:
    """
    Imports all importable files from a specified directory
    
    :param query:       Query the directory (don't import anything).
    :param reset:       Whether to clear data from the model first.
    :param directory:   Directory to import
    :param filter:      Filter on import
    """
    if reset:
        if not query:
            workflow.s010_file.file_new()
        else:
            MCMD.print( "Importing will start a new model." )
    
    model = global_view.current_model()
    contents = file_helper.list_dir( directory )
    
    if filter.DATA:
        for file_name in contents:
            import_file( model, file_name, skip_bad_extensions = True, filter = EImportFilter.DATA, query = query )
    
    if filter.SCRIPT:
        for file_name in contents:
            import_file( model, file_name, skip_bad_extensions = True, filter = EImportFilter.SCRIPT, query = query )
    
    if query:
        return EChanges.NONE
    
    if reset:
        if MCMD.host.is_cli:
            console_explorer.re_cd( VisualisablePath.get_root() )
        
        return EChanges.MODEL_OBJECT
    else:
        return EChanges.MODEL_ENTITIES
