from PyQt5.QtWidgets import QVBoxLayout, QRadioButton, QSpacerItem, QSizePolicy, QWidget
from groot.utilities.extendable_algorithm import AlgorithmCollection
from groot_gui.forms.designer import frm_run_algorithm_designer
from typing import Tuple, Callable

from groot_gui.forms.frm_base import FrmBase
import groot
import editorium
import intermake
from groot_gui.utilities.gui_workflow import Intent
from mhelper import FunctionInspector, ArgValueCollection, NOT_PROVIDED
import mhelper_qt as qt


class FrmRunAlgorithm( FrmBase ):
    """
    The user can select an algorithm from this screen.
    
    The set of algorithms available depends upon the command being executed and the
    plugins/extensions the user has installed.
    """
    
    
    @qt.exceptToGui()
    def __init__( self,
                  parent: QWidget,
                  title_text: str,
                  algorithms: AlgorithmCollection,
                  plugin: intermake.AbstractCommand ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_run_algorithm_designer.Ui_Dialog( self )
        self.setWindowTitle( title_text )
        self.editorium = editorium.EditoriumGrid( self.ui.FRA_PARAMETERS )
        self.ui.LBL_TITLE.setText( "Create " + title_text.lower() )
        self.radios = []
        self.algorithms = algorithms
        self.command: intermake.AbstractCommand = plugin
        
        self.__layout = QVBoxLayout()
        self.ui.FRA_MAIN.setLayout( self.__layout )
        
        for name, function in self.algorithms:
            self.add_radio( name )
        
        self.__layout.addItem( QSpacerItem( 0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding ) )
        
        self.bind_to_label( self.ui.LBL_WARN_REQUIREMENTS )
        self.ui.LBL_HELP.setVisible( False )
        self.allow_proceed = False
        self.update_labels()
    
    
    def on_apply_request( self, intent: Intent ):
        if intent.is_inspect:
            if isinstance( intent.target, groot.AbstractAlgorithm ):
                algo: groot.AbstractAlgorithm = intent.target
                
                for cb in self.radios:
                    assert isinstance( cb, QRadioButton )
                    if cb.toolTip() == algo.name:
                        cb.setChecked( True )
                        return
            else:
                intent.warn()
    
    
    def add_radio( self, name ):
        rad = QRadioButton()
        rad.setText( name )
        rad.setToolTip( name )
        rad.toggled[bool].connect( self.on_radio_toggled )
        self.radios.append( rad )
        self.__layout.addWidget( rad )
    
    
    def on_radio_toggled( self, _: bool ):
        self.update_labels()
    
    
    def on_command_completed( self ):
        self.update_labels()
    
    
    def update_labels( self ):
        # Ask derived class if we are ready
        ready, message = self.on_query_ready()
        
        # Get our algorithm name
        algo_name = self.__get_selected_algorithm_name( default = None )
        algo_fn: Callable = self.algorithms.get_function( algo_name )
        
        if algo_fn is None:
            ready = False
        
        # Show some help
        self.ui.LBL_HELP.setVisible( algo_fn is not None )
        
        if algo_fn is not None:
            doc = algo_fn.__doc__ if hasattr( algo_fn, "__doc__" ) else "This algorithm has not been documented."
            self.ui.LBL_HELP.setText( doc )
        
        # Show the requirements warning?
        self.ui.LBL_WARN_REQUIREMENTS.setText( message )
        self.ui.LBL_WARN_REQUIREMENTS.setVisible( bool( message ) )
        
        # Enable the OK button
        self.ui.BTN_OK.setEnabled( ready )
        
        # Populate the arguments list
        self.editorium.target = ArgValueCollection( x for x in FunctionInspector( algo_fn ).args if x.index >= self.algorithms.num_expected_args ) if algo_fn is not None else None
        self.editorium.recreate()
        
        self.actions.adjust_window_size()
    
    
    def on_query_ready( self ) -> Tuple[bool, str]:
        raise NotImplementedError( "abstract" )
    
    
    def run_algorithm( self, algorithm: groot.AbstractAlgorithm ):
        self.actions.run( self.command, algorithm ).listen( self.run_algorithm_completed )
    
    
    def run_algorithm_completed( self, result: intermake.AsyncResult ):
        if result.is_success:
            self.actions.close_window()
    
    
    @qt.exqtSlot()
    def on_BTN_OK_clicked( self ) -> None:
        """
        Signal handler:
        """
        algo_name = self.__get_selected_algorithm_name()
        
        self.editorium.commit()
        avc: ArgValueCollection = self.editorium.target
        
        algorithm: groot.AbstractAlgorithm = self.algorithms.get_algorithm( algo_name, **avc.tokwargs() )
        self.run_algorithm( algorithm )
    
    
    @qt.exqtSlot()
    def on_BTN_HELP_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_my_help()
    
    
    def __get_selected_algorithm_name( self, default = NOT_PROVIDED ) -> str:
        for rad in self.radios:
            assert isinstance( rad, QRadioButton )
            if rad.isChecked():
                return rad.toolTip()
        
        if default is NOT_PROVIDED:
            raise ValueError( "No algorithm selected." )
        else:
            return default


class FrmCreateTrees( FrmRunAlgorithm ):
    def on_query_ready( self ):
        model = self.get_model()
        
        if model.get_status( groot.constants.STAGES.TREES_6 ).is_complete:
            return False, '<html><body>Trees already exist, you can <a href="action:view_trees">view the trees</a>, <a href="action:drop_trees">remove them</a> or proceed to <a href="action:create_fusions">finding the fusions</a>.</body></html>'
        
        if model.get_status( groot.constants.STAGES.ALIGNMENTS_5 ).is_not_complete:
            return False, '<html><body>You need to <a href="action:create_alignments">create the alignments</a> before creating the trees.</body></html>'
        
        if model.get_status( groot.constants.STAGES.OUTGROUPS_5b ).is_not_complete:
            return True, '<html><body>You do not have any <a href="action:view_entities">outgroups</a> set, your trees will be unrooted!</body></html>'
        
        return True, ""
    
    
    @qt.exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Trees",
                          groot.tree_algorithms,
                          groot.create_trees )


class FrmCreateAlignment( FrmRunAlgorithm ):
    def on_query_ready( self ):
        model = self.get_model()
        
        if model.get_status( groot.constants.STAGES.ALIGNMENTS_5 ).is_complete:
            return False, '<html><body>Alignments already exist, you can <a href="action:view_alignments">view the alignments</a>, <a href="action:drop_alignments">remove them</a> or proceed to <a href="action:create_trees">creating the trees</a>.</body></html>'
        
        if model.get_status( groot.constants.STAGES.MINOR_3 ).is_not_complete:
            return False, '<html><body>You need to <a href="action:create_major">create the components</a> before creating the alignments.</body></html>'
        
        return True, ""
    
    
    @qt.exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Alignments",
                          groot.alignment_algorithms,
                          groot.create_alignments )


class FrmCreateSubgraphs( FrmRunAlgorithm ):
    def on_query_ready( self ):
        model = self.get_model()
        
        if model.get_status( groot.constants.STAGES.SUBGRAPHS_11 ).is_complete:
            return False, '<html><body>Subgraphs already exist, you can <a href="action:view_trees">view the trees</a>, <a href="action:drop_subgraphs">remove them</a> or proceed to <a href="action:create_fused">creating the fused graph</a>.</body></html>'
        
        if model.get_status( groot.constants.STAGES.SUBSETS_10 ).is_not_complete:
            return False, '<html><body>You need to <a href="action:create_subsets">create the components</a> before creating the subgraphs.</body></html>'
        
        return True, ""
    
    
    @qt.exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Subgraphs",
                          groot.supertree_algorithms,
                          groot.create_supertrees )


class FrmCreateDomains( FrmRunAlgorithm ):
    def on_query_ready( self ):
        model = self.get_model()
        
        if model.get_status( groot.constants.STAGES._DATA_0 ).is_none:
            return False, '<html><body>You need to <a href="action:import_file">import some data</a> before creating the domains.</body></html>'
        
        return True, ""
    
    
    @qt.exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Domains",
                          groot.domain_algorithms,
                          groot.create_domains )
