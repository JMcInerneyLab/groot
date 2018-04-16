from PyQt5.QtWidgets import QVBoxLayout, QRadioButton, QSpacerItem, QSizePolicy, QWidget
from groot.utilities.extendable_algorithm import AlgorithmCollection
from groot.frontends.gui.forms.designer import frm_run_algorithm_designer
from typing import Tuple

from groot import algorithms
from groot.frontends.gui.forms.frm_base import FrmBase
from groot import ext_generating, constants
from intermake.engine.plugin import Plugin
from mhelper_qt import exceptToGui, exqtSlot


class FrmRunAlgorithm( FrmBase ):
    @exceptToGui()
    def __init__( self,
                  parent: QWidget,
                  title_text: str,
                  algorithms: AlgorithmCollection,
                  plugin: Plugin ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_run_algorithm_designer.Ui_Dialog( self )
        self.setWindowTitle( title_text )
        self.ui.LBL_TITLE.setText( "Create " + title_text.lower() )
        self.radios = []
        self.algorithms = algorithms
        self.plugin: Plugin = plugin
        
        self.__layout = QVBoxLayout()
        self.ui.FRA_MAIN.setLayout( self.__layout )
        
        for name, function in self.algorithms:
            self.add_radio( name )
        
        self.__layout.addItem( QSpacerItem( 0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding ) )
        
        self.bind_to_label( self.ui.LBL_WARN_REQUIREMENTS )
        self.ui.LBL_HELP.setVisible( False )
        self.allow_proceed = False
        self.update_labels()
    
    
    def add_radio( self, name ):
        rad = QRadioButton()
        rad.setText( name )
        rad.setToolTip( name )
        rad.toggled[bool].connect( self.on_radio_toggled )
        self.radios.append( rad )
        self.__layout.addWidget( rad )
    
    
    def on_radio_toggled( self, _: bool ):
        self.update_labels()
    
    
    def on_plugin_completed( self ):
        if self.actions.frm_main.completed_plugin is self.plugin:
            self.actions.close_window()
        else:
            self.update_labels()
    
    
    def update_labels( self ):
        ready, message = self.query_ready()
        function = None
        
        for rad in self.radios:
            assert isinstance( rad, QRadioButton )
            
            if rad.isChecked():
                function = self.algorithms[rad.toolTip()]
            
            rad.setEnabled( ready )
        
        if function is None:
            ready = False
        
        self.ui.LBL_HELP.setVisible( function is not None )
        
        if function is not None:
            doc = function.__doc__ if hasattr( function, "__doc__" ) else "This algorithm has not been documented."
            self.ui.LBL_HELP.setText( doc )
        
        self.ui.LBL_WARN_REQUIREMENTS.setText( message )
        self.ui.LBL_WARN_REQUIREMENTS.setVisible( bool( message ) )
        self.ui.BTN_OK.setEnabled( ready )
        
        self.actions.adjust_window_size()
    
    
    def query_ready( self ) -> Tuple[bool, str]:
        raise NotImplementedError( "abstract" )
    
    
    def run_algorithm( self, key: str ):
        self.plugin.run( key )
    
    
    @exqtSlot()
    def on_BTN_OK_clicked( self ) -> None:
        """
        Signal handler:
        """
        algo = None
        
        for rad in self.radios:
            assert isinstance( rad, QRadioButton )
            if rad.isChecked():
                algo = rad.toolTip()
        
        self.run_algorithm( algo )


class FrmCreateTrees( FrmRunAlgorithm ):
    def query_ready( self ):
        model = self.get_model()
        
        if model.get_status( constants.STAGES.TREES_6 ).is_complete:
            return False, '<html><body>Trees already exist, you can <a href="action:view_trees">view the trees</a>, <a href="action:drop_trees">remove them</a> or proceed to <a href="action:create_fusions">finding the fusions</a>.</body></html>'
        
        if model.get_status( constants.STAGES.ALIGNMENTS_5 ).is_not_complete:
            return False, '<html><body>You need to <a href="action:create_alignments">create the alignments</a> before creating the trees.</body></html>'
        
        if model.get_status( constants.STAGES.OUTGROUPS_5b ).is_not_complete:
            return True, '<html><body>You do not have any <a href="action:view_entities">outgroups</a> set, your trees will be unrooted!</body></html>'
        
        return True, ""
    
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Trees",
                          algorithms.s080_tree.tree_algorithms,
                          ext_generating.create_trees )


class FrmCreateAlignment( FrmRunAlgorithm ):
    def query_ready( self ):
        model = self.get_model()
        
        if model.get_status( constants.STAGES.ALIGNMENTS_5 ).is_complete:
            return False, '<html><body>Alignments already exist, you can <a href="action:view_alignments">view the alignments</a>, <a href="action:drop_alignments">remove them</a> or proceed to <a href="action:create_trees">creating the trees</a>.</body></html>'
        
        if model.get_status( constants.STAGES.MINOR_3 ).is_not_complete:
            return False, '<html><body>You need to <a href="action:create_major">create the components</a> before creating the alignments.</body></html>'
        
        return True, ""
    
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Alignments",
                          algorithms.s070_alignment.alignment_algorithms,
                          ext_generating.create_alignments )

class FrmCreateSubgraphs( FrmRunAlgorithm ):
    def query_ready( self ):
        model = self.get_model()
        
        if model.get_status( constants.STAGES.SUBGRAPHS_11 ).is_complete:
            return False, '<html><body>Subgraphs already exist, you can <a href="action:view_trees">view the trees</a>, <a href="action:drop_subgraphs">remove them</a> or proceed to <a href="action:create_fused">creating the fused graph</a>.</body></html>'
        
        if model.get_status( constants.STAGES.SUBSETS_10 ).is_not_complete:
            return False, '<html><body>You need to <a href="action:create_subsets">create the components</a> before creating the subgraphs.</body></html>'
        
        return True, ""
    
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Subgraphs",
                          algorithms.s140_supertrees.supertree_algorithms,
                          ext_generating.create_subgraphs )

class FrmCreateDomains( FrmRunAlgorithm ):
    def query_ready( self ):
        model = self.get_model()
        
        if model.get_status( constants.STAGES._DATA_0 ).is_none:
            return False, '<html><body>You need to <a href="action:import_file">import some data</a> before creating the domains.</body></html>'
        
        
        return True, ""
    
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Domains",
                          algorithms.s060_userdomains.domain_algorithms,
                          ext_generating.create_domains )
