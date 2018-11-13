from warnings import warn

from intermake import Command, Theme, commands, visibilities, BasicCommand, pr
from mhelper import EFileMode, isFilename, MFlags, file_helper, ManagedWith
from typing import List, Optional, cast, Set

from groot import constants
from groot.application import app
from groot.commands import workflow
from groot.constants import EFormat, Stage, STAGES, EChanges
from groot.data import global_view




class EImportFilter( MFlags ):
    """
    Mask on importing files.
    
    :cvar DATA: Data files (constants.EXT_FASTA, constants.EXT_BLAST)
    :cvar MODEL: Model files (constants.EXT_MODEL)
    :cvar SCRIPT: Scripts
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
                  pauses: Set[Stage],
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
        self.pauses = pauses
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
        r.append( "pauses            = {}".format( self.pauses ) )
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
        pr.pr_verbose( "Walkthrough has paused after {}{}{} due to user request.".format( Theme.BOLD, title, Theme.RESET ) )
        pr.pr_verbose( "Use the following commands to review:" )
        for command in commands:
            pr.pr_verbose( "* {}{}{}".format( Theme.COMMAND_NAME,
                                              cast( Command, command ).name,
                                              Theme.RESET ) )
        pr.pr_verbose( "Use the {}{}{} command to continue the wizard.".format( Theme.COMMAND_NAME,
                                                                                cast( Command, continue_wizard ).name,
                                                                                Theme.RESET ) )
        self.is_paused = True
    
    
    def __start_line( self, title: object ):
        title = "WIZARD: " + str( title )
        pr.printx( '<section name="">'.format( title ) )
        return ManagedWith( on_exit = self.__end_line )
    
    
    def __end_line( self, _ : None ):
        pr.printx( '</section>' )
    
    
    def get_stage_name( self ):
        return self.__stages[self.__stage].__name__
    
    
    def stop( self ):
        Wizard.__active_walkthrough = None
        pr.pr_verbose( "The active wizard has been deleted." )
    
    
    def step( self ) -> EChanges:
        """
        Steps the Wizard forward until the next requested `pause`.
        If this completes the Wizard, `is_completed` will now return `True`.
        
        :return: Summary of changes made.
        """
        if self.is_completed:
            raise ValueError( "The wizard has already completed." )
        
        self.is_paused = False
        self.__result = EChanges.NONE
        
        while not self.is_paused and self.__stage < len( self.__stages ):
            self.__stages[self.__stage]( self )
            self.__stage += 1
            self.__save_model()
        
        if self.__stage == len( self.__stages ):
            pr.pr_verbose( "The wizard is complete." )
            self.is_completed = True
        
        return self.__result
    
    
    def __fn8_make_splits( self ):
        with self.__start_line( STAGES.SPLITS_10 ):
            workflow.s100_splits.create_splits()
        
        if STAGES.SPLITS_10 in self.pauses:
            self.__pause( STAGES.SPLITS_10, (workflow.s100_splits.print_splits,) )
    
    
    def __fn9_make_consensus( self ):
        with self.__start_line( STAGES.CONSENSUS_11 ):
            workflow.s110_consensus.create_consensus()
        
        if STAGES.CONSENSUS_11 in self.pauses:
            self.__pause( STAGES.CONSENSUS_11, (workflow.s110_consensus.print_consensus,) )
    
    
    def __fn10_make_subsets( self ):
        with self.__start_line( STAGES.SUBSETS_12 ):
            workflow.s120_subsets.create_subsets()
        
        if STAGES.SUBSETS_12 in self.pauses:
            self.__pause( STAGES.SUBSETS_12, (workflow.s120_subsets.print_subsets,) )
    
    
    def __fn12_make_subgraphs( self ):
        with self.__start_line( "Subgraphs" ):
            algo = workflow.s140_supertrees.supertree_algorithms.get_algorithm( self.supertree )
            workflow.s140_supertrees.create_supertrees( algo )
        
        if STAGES.SUPERTREES_14 in self.pauses:
            self.__pause( STAGES.SUPERTREES_14, (workflow.s140_supertrees.print_supertrees,) )
    
    
    def __fn11_make_pregraphs( self ):
        with self.__start_line( "Pregraphs" ):
            workflow.s130_pregraphs.create_pregraphs()
        
        if STAGES.PREGRAPHS_13 in self.pauses:
            self.__pause( STAGES.PREGRAPHS_13, (workflow.s130_pregraphs.print_pregraphs,) )
    
    
    def __fn13_make_fused( self ):
        with self.__start_line( STAGES.FUSE_15 ):
            workflow.s150_fuse.create_fused()
        
        if STAGES.FUSE_15 in self.pauses:
            self.__pause( STAGES.FUSE_15, (workflow.s080_tree.print_trees,) )
    
    
    def __fn14_make_clean( self ):
        with self.__start_line( STAGES.CLEAN_16 ):
            workflow.s160_clean.create_cleaned()
        
        if STAGES.CLEAN_16 in self.pauses:
            self.__pause( STAGES.CLEAN_16, (workflow.s080_tree.print_trees,) )
    
    
    def __fn15_make_checks( self ):
        with self.__start_line( STAGES.CHECKED_17 ):
            workflow.s170_checked.create_checked()
        
        if STAGES.CHECKED_17 in self.pauses:
            self.__pause( STAGES.CHECKED_17, (workflow.s080_tree,) )
    
    
    def __fn16_view_nrfg( self ):
        if self.view:
            self.__result |= workflow.s080_tree.print_trees( graph = global_view.current_model().fusion_graph_clean.graph,
                                                             format = EFormat.VISJS,
                                                             file = "open" )
    
    
    def __fn7_make_fusions( self ):
        # Make fusions
        with self.__start_line( STAGES.FUSIONS_9 ):
            self.__result |= workflow.s090_fusion_events.create_fusions()
        
        if STAGES.FUSIONS_9 in self.pauses:
            self.__pause( STAGES.FUSIONS_9, (workflow.s080_tree.print_trees, workflow.s090_fusion_events.print_fusions) )
    
    
    def __fn6_make_trees( self ):
        with self.__start_line( STAGES.TREES_8 ):
            model = global_view.current_model()
            ogs = [model.genes[x] for x in self.outgroups]
            
            self.__result |= workflow.s055_outgroups.set_outgroups( ogs )
            
            algo = workflow.s080_tree.tree_algorithms.get_algorithm( self.tree )
            self.__result |= workflow.s080_tree.create_trees( algo )
        
        if STAGES.TREES_8 in self.pauses:
            self.__pause( STAGES.TREES_8, (workflow.s080_tree.print_trees,) )
    
    
    def __fn5_make_alignments( self ):
        with self.__start_line( STAGES.ALIGNMENTS_7 ):
            algo = workflow.s070_alignment.alignment_algorithms.get_algorithm( self.alignment )
            self.__result |= workflow.s070_alignment.create_alignments( algo )
        
        if STAGES.ALIGNMENTS_7 in self.pauses:
            self.__pause( STAGES.ALIGNMENTS_7, (workflow.s070_alignment.print_alignments,) )
    
    
    def __fn4_make_major( self ):
        with self.__start_line( STAGES.MAJOR_4 ):
            self.__result |= workflow.s040_major.create_major( self.tolerance )
        
        if STAGES.MAJOR_4 in self.pauses:
            self.__pause( STAGES.MAJOR_4, (workflow.s020_sequences.print_genes, workflow.s040_major.print_major) )
    
    
    def __fn4_make_minor( self ):
        with self.__start_line( STAGES.MINOR_5 ):
            self.__result |= workflow.s050_minor.create_minor( self.tolerance )
        
        if STAGES.MINOR_5 in self.pauses:
            self.__pause( STAGES.MINOR_5, (workflow.s020_sequences.print_genes, workflow.s050_minor.print_minor) )
    
    
    def __fn4b_make_domains( self ):
        with self.__start_line( STAGES.DOMAINS_6 ):
            algo = workflow.s060_userdomains.domain_algorithms.get_algorithm( "component" )
            self.__result |= workflow.s060_userdomains.create_domains( algo )
    
    
    def __fn3_import_data( self ):
        with self.__start_line( STAGES.SEQ_AND_SIM_ps ):
            for import_ in self.imports:
                self.__result |= import_file( import_ )
        
        if STAGES.SEQ_AND_SIM_ps in self.pauses:
            self.__pause( STAGES.SEQ_AND_SIM_ps, (workflow.s020_sequences.print_genes,) )
    
    
    def __save_model( self ):
        if self.save:
            with self.__start_line( STAGES._FILE_0 ):
                self.__result |= workflow.s010_file.file_save( self.name )
    
    
    def __fn1_new_model( self ):
        # Start a new model
        with self.__start_line( "New" ):
            if self.new:
                self.__result |= workflow.s010_file.file_new()
    
    
    def make_active( self ) -> None:
        """
        Sets this `Wizard` object as the active (currently running) wizard.
        This is called by the `create_wizard` command after constructing the wizard.
        """
        Wizard.__active_walkthrough = self
        pr.pr_verbose( "{}".format( str( self ) ) )
        pr.pr_verbose( "The wizard has been activated and is paused. Use the {}{}{} function to begin.".format(
                Theme.COMMAND_NAME,
                BasicCommand.retrieve( continue_wizard ),
                Theme.RESET ) )
    
    
    @staticmethod
    def get_active() -> Optional["Wizard"]:
        """
        Gets the active `Wizard` object (which may be `None`).
        """
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


@app.command( folder = constants.F_CREATE )
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
                   pause: str = None ) -> None:
    """
    Sets up a workflow that you can activate in one go.
    
    If you don't fill out the parameters then whatever UI you are using will prompt you for them.
    
    If you have a set of default parameters that you'd like to preserve, take a look at the `alias` command.
    
    This method is represented in the GUI by the wizard window.
    
    :param new:                 Create a new model?
                                :values:`true→yes, false→no, none→ask` 
    :param name:                Name the model?
                                You can specify a complete path or just a name.
                                If no name (empty) is specified, then the model is not saved.
                                :values:`empty→no name, none→ask`
    :param outgroups:           Outgroup accessions?
                                :values:`none→ask`
    :param imports:             Import files into the model?
                                :values:`none→ask` 
    :param tolerance:           Component identification tolerance?
                                :values:`none→ask` 
    :param alignment:           Alignment method?
                                :values:`empty→default, none→ask`
    :param supertree:           Supertree method? 
                                :values:`empty→default,none→ask`
    :param tree:                Tree generation method?
                                :values:`empty→default, none→ask`
    :param view:                View the final NRFG in Vis.js?
                                :values:`true→yes, false→no, none→ask` 
    :param save:                Save file to disk? (requires `name`)
                                :values:`true→yes, false→no, none→ask` 
    :param pause:               Pause after stage default value.
                                :values:`none→ask`
    """
    if new is None:
        x = pr.pr_question( "Are you starting a new model, or do you want to continue with your current data?", ["new", "continue"] )
        new = (x == "new")
    
    if name is None:
        name = pr.pr_question( "Name your model.\n"
                         "You can specify a complete path or just a name.\n"
                         "If you don't enter a name, your won't have the option to save your file using the wizard, though you can still do so manually." )
        
        if not name:
            warn( "Your file will not be saved by the wizard.", UserWarning )
    
    if imports is None:
        imports = []
        
        while True:
            ex = "\nEnter a blank line when you don't want to add any more files." if imports else ""
            file_name = pr.pr_question( "Enter file paths to import BLAST or FASTA files, one per line." + ex )
            
            if file_name:
                imports.append( file_name )
            else:
                break
    
    if outgroups is None:
        outgroups = []
        
        while True:
            ex = "\nEnter a blank line when you don't want to add any more outgroups."
            outgroup = pr.pr_question( "Enter outgroup accessions, one per line." + ex )
            
            if outgroup:
                outgroups.append( outgroup )
            else:
                break
    
    if tolerance is None:
        success = False
        
        while not success:
            tolerance_str = pr.pr_question( "What tolerance do you want to use for the component identification?" )
            
            try:
                tolerance = int( tolerance_str )
                success = True
            except:
                pr.printx( "Something went wrong. Let's try that question again." )
                success = False
    
    if alignment is None:
        alignment = pr.pr_question( "Which function do you want to use for the sequence alignment? Enter a blank line for the default.", list( workflow.s070_alignment.alignment_algorithms.keys ) + [""] )
    
    if tree is None:
        tree = pr.pr_question( "Which function do you want to use for the tree generation? Enter a blank line for the default.", list( workflow.s080_tree.tree_algorithms.keys ) + [""] )
    
    if supertree is None:
        supertree = pr.pr_question( "Which function do you want to use for the supertree generation? Enter a blank line for the default.", list( workflow.s140_supertrees.supertree_algorithms.keys ) + [""] )
    
    pauses = set()
    
    map = { "i": STAGES.SEQ_AND_SIM_ps,
            "m": STAGES.MAJOR_4,
            "d": STAGES.MINOR_5,
            "a": STAGES.ALIGNMENTS_7,
            "t": STAGES.TREES_8,
            "f": STAGES.FUSIONS_9,
            "S": STAGES.SPLITS_10,
            "C": STAGES.CONSENSUS_11,
            "e": STAGES.SUBSETS_12,
            "p": STAGES.PREGRAPHS_13,
            "s": STAGES.SUPERTREES_14,
            "u": STAGES.FUSE_15,
            "n": STAGES.CLEAN_16,
            "c": STAGES.CHECKED_17 }
    
    if pause is None:
        for k, v in map.items():
            pr.printx( "<key>{}</key> = <value>{}</value>".format( pr.escape( k),pr.escape( v) ) )
        
        pause = pr.pr_question( "Enter pauses (as above):" )
    
    for c in pause:
        if c in map:
            pauses.add( map[c] )
        else:
            raise ValueError( "Unknown pause command: {} in {}".format( repr( c ), repr( pause ) ) )
    
    if view is None:
        view = pr.pr_question( "Do you wish the wizard to show you the final NRFG in Vis.js?" )
    
    if save is None:
        if not name:
            save = False
        else:
            save = pr.pr_question( "Save your model after each stage completes?" )
    
    walkthrough = Wizard( new = new,
                          name = name,
                          imports = imports,
                          pauses = pause,
                          tolerance = tolerance,
                          alignment = alignment,
                          tree = tree,
                          view = view,
                          save = save,
                          outgroups = outgroups,
                          supertree = supertree )
    
    walkthrough.make_active()
    pr.pr_verbose( "The wizard has been created paused.\nYou can use the {} and {} commands to manage your wizard.".format( continue_wizard, drop_wizard ) )


@app.command( visibility = visibilities.ADVANCED, names = ["continue"], folder = constants.F_EXTRA )
def continue_wizard() -> EChanges:
    """
    Continues the wizard after it was paused.
    """
    if Wizard.get_active() is None:
        raise ValueError( "There is no active wizard to continue." )
    
    pr.pr_verbose( "The wizard has been resumed." )
    
    return Wizard.get_active().step()


@app.command( visibility = visibilities.ADVANCED, names = ["stop"], folder = constants.F_DROP )
def drop_wizard() -> EChanges:
    """
    Stops a wizard.
    """
    if Wizard.get_active() is None:
        raise ValueError( "There is no active wizard to stop." )
    
    Wizard.get_active().stop()
    return EChanges.NONE


@app.command( folder = constants.F_CREATE )
def create_components( tol: int = 0 ):
    """
    Executes `create_major` then `create_minor`.
    :param tol: Tolerance
    """
    return (workflow.s040_major.create_major( tol ) |
            workflow.s050_minor.create_minor( tol ))


@app.command( folder = constants.F_DROP )
def drop_components() -> EChanges:
    """
    Removes all the components from the model.
    """
    count = workflow.s040_major.drop_major()
    
    pr.pr_verbose( "Dropped all {} components from the model.".format( count ) )
    
    return EChanges.COMPONENTS


@app.command( folder = constants.F_IMPORT )
def import_file( file_name: isFilename[EFileMode.READ],
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
    :param query:                   When set the kind of the file is printed to `sys.stdout` and the file is not imported. 
    :return:                        Nothing is returned, the file data is incorporated into the model and messages are sent via `sys.stdout`.
    """
    ext = file_helper.get_extension( file_name ).lower()
    
    if filter.DATA:
        if ext == ".blast":
            if not query:
                return workflow.s030_similarity.import_similarities( file_name )
            else:
                pr.printx( "BLAST: <file>{}</file>.".format( pr.escape( file_name) ) )
                return EChanges.INFORMATION
        elif ext in (".fasta", ".fa", ".faa"):
            if not query:
                return workflow.s020_sequences.import_genes( file_name )
            else:
                pr.printx( "FASTA: <file>{}</file>.".format( pr.escape(file_name )) )
                return EChanges.INFORMATION
    
    if filter.SCRIPT:
        if ext == ".imk":
            if not query:
                pr.printx( "<verbose>Run script <file>{}</file>.</verbose>".format( pr.escape(file_name) ) )
                commands.execute_cli_text( file_name )
                return EChanges.MODEL_OBJECT
            else:
                pr.printx( "Script: <file>{}</file>.".format( pr.escape(file_name) ) )
                return EChanges.INFORMATION
    
    if filter.MODEL:
        if ext == constants.EXT_MODEL:
            if not query:
                return workflow.s010_file.file_load( file_name )
            else:
                pr.printx( "Model: <file>{}</file>.".format( pr.escape(file_name) ) )
                return EChanges.INFORMATION
    
    if skip_bad_extensions:
        return EChanges.NONE
    
    raise ValueError( "Cannot import the file '{}' because I don't recognise the extension '{}'.".format( file_name, ext ) )


@app.command( folder = constants.F_IMPORT )
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
            pr.printx( "Importing will start a new model." )
    
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
        return EChanges.MODEL_OBJECT
    else:
        return EChanges.MODEL_ENTITIES
