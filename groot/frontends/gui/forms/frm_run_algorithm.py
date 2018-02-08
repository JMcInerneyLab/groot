from PyQt5.QtWidgets import QVBoxLayout, QRadioButton, QSpacerItem, QSizePolicy
from groot.frontends.gui.forms.designer import frm_run_algorithm_designer

from groot.algorithms import external_runner
from groot.algorithms.external_runner import EAlgoType
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
from groot import ext_generating
from mhelper_qt import exceptToGui, exqtSlot


class FrmRunAlgorithm( FrmBase ):
    @exceptToGui()
    def __init__( self, parent, title, algo_type, prereq, exists ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_run_algorithm_designer.Ui_Dialog( self )
        self.setWindowTitle( title )
        self.radios = []
        
        algos = external_runner.list_algorithms()
        
        layout = QVBoxLayout()
        self.ui.FRA_MAIN.setLayout( layout )
        
        for prefix, function in algos[algo_type].items():
            rad = QRadioButton()
            rad.setText( prefix )
            rad.toggled[bool].connect( self.on_radio_toggled )
            self.radios.append( rad )
            rad.TAG_function = function
            layout.addWidget( rad )
        
        layout.addItem( QSpacerItem( 0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding ) )
        
        self.ui.LBL_WARN_ALREADY.setText( exists )
        self.ui.LBL_WARN_REQUIREMENTS.setText( prereq )
        self.actions.bind_to_label( self.ui.LBL_WARN_ALREADY )
        self.actions.bind_to_label( self.ui.LBL_WARN_REQUIREMENTS )
        self.ui.LBL_HELP.setVisible( False )
        self.update_labels()
    
    
    def on_radio_toggled( self, checked: bool ):
        if not checked:
            return
        
        self.ui.LBL_HELP.setVisible( True )
        function = self.sender().TAG_function
        doc = function.__doc__ if hasattr( function, "__doc__" ) else "This algorithm has not been documented."
        self.ui.LBL_HELP.setText( doc )
    
    
    def on_plugin_completed( self, change: EChanges ):
        self.update_labels()
    
    
    def update_labels( self ):
        self.ui.LBL_WARN_REQUIREMENTS.setVisible( not self.query_ready() )
        self.ui.LBL_WARN_ALREADY.setVisible( self.query_exists() )
    
    
    def query_exists( self ):
        raise NotImplementedError( "abstract" )
    
    
    def query_ready( self ):
        raise NotImplementedError( "abstract" )
    
    
    def run_algorithm( self, key: str ):
        raise NotImplementedError( "abstract" )
    
    
    @exqtSlot()
    def on_BTN_OK_clicked( self ) -> None:
        """
        Signal handler:
        """
        algo = None
        
        for rad in self.radios:
            assert isinstance( rad, QRadioButton )
            if rad.isChecked():
                algo = rad.text()
        
        self.run_algorithm( algo )


class FrmCreateTrees( FrmRunAlgorithm ):
    def run_algorithm( self, key: str ):
        ext_generating.make_trees( key )
    
    
    def query_exists( self ):
        return bool( self.get_model().components ) and all( x.tree for x in self.get_model().components )
    
    
    def query_ready( self ):
        return bool( self.get_model().components ) and all( x.alignment for x in self.get_model().components )
    
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Trees",
                          EAlgoType.TREE,
                          '<html><body>You need to <a href="action:create_alignments">create the alignments</a> before creating the trees.</body</html>',
                          '<html><body>Trees already exist, you can <a href="action:show_trees">view the trees</a>, <a href="action:drop_trees">remove them</a> or proceed to <a href="action:create_fusions">finding the fusions</a>.</body</html>' )


class FrmCreateAlignment( FrmRunAlgorithm ):
    def run_algorithm( self, key: str ):
        ext_generating.make_alignments( key )
    
    
    def query_exists( self ):
        return bool( self.get_model().components ) and all( x.alignment for x in self.get_model().components )
    
    
    def query_ready( self ):
        return bool( self.get_model().components )
    
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent,
                          "Alignments",
                          EAlgoType.ALIGN,
                          '<html><body>You need to <a href="action:create_components">create the components</a> before creating the alignments.</body</html>',
                          '<html><body>Alignments already exist, you can <a href="action:show_alignments">view the alignments</a>, <a href="action:drop_alignments">remove them</a> or proceed to <a href="action:create_trees">creating the trees</a>.</body</html>' )
