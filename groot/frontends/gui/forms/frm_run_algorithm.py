from PyQt5.QtWidgets import QVBoxLayout, QRadioButton, QSpacerItem, QSizePolicy, QWidget
from groot.frontends.gui.forms.designer import frm_run_algorithm_designer
from typing import Any

from groot.algorithms import tree, alignment
from groot.frontends.gui.forms.frm_base import FrmBase
from groot import ext_generating
from intermake.engine.plugin import Plugin
from mhelper_qt import exceptToGui, exqtSlot


class FrmRunAlgorithm( FrmBase ):
    @exceptToGui()
    def __init__( self,
                  parent: QWidget,
                  title_text: str,
                  prerequisite_text: str,
                  exists_text: str,
                  algorithm_module: Any,
                  plugin: Plugin ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_run_algorithm_designer.Ui_Dialog( self )
        self.setWindowTitle( title_text )
        self.ui.LBL_TITLE.setText( "Create " + title_text.lower() )
        self.radios = []
        self.algorithms = algorithm_module.algorithms
        self.plugin: Plugin = plugin
        
        layout = QVBoxLayout()
        self.ui.FRA_MAIN.setLayout( layout )
        
        for name, function in self.algorithms.items():
            rad = QRadioButton()
            rad.setText( name )
            rad.setToolTip( name )
            rad.toggled[bool].connect( self.on_radio_toggled )
            self.radios.append( rad )
            layout.addWidget( rad )
        
        layout.addItem( QSpacerItem( 0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding ) )
        
        self.ui.LBL_WARN_ALREADY.setText( exists_text )
        self.ui.LBL_WARN_REQUIREMENTS.setText( prerequisite_text )
        self.bind_to_label( self.ui.LBL_WARN_ALREADY )
        self.bind_to_label( self.ui.LBL_WARN_REQUIREMENTS )
        self.ui.LBL_HELP.setVisible( False )
        self.allow_proceed = False
        self.update_labels()
    
    
    def on_radio_toggled( self, _: bool ):
        self.update_labels()
    
    
    def on_plugin_completed( self ):
        if self.actions.frm_main.completed_plugin is self.plugin:
            self.actions.close_window()
        else:
            self.update_labels()
    
    
    def update_labels( self ):
        requirements_met = self.query_ready()
        doesnt_exist = not self.query_exists()
        ready = requirements_met and doesnt_exist
        function = None
        
        for rad in self.radios:
            assert isinstance( rad, QRadioButton )
            
            if rad.isChecked():
                function = self.algorithms[rad.toolTip()]
            
            rad.setEnabled( ready )
        
        self.ui.LBL_HELP.setVisible( function is not None )
        
        if function is not None:
            doc = function.__doc__ if hasattr( function, "__doc__" ) else "This algorithm has not been documented."
            self.ui.LBL_HELP.setText( doc )
        
        self.ui.LBL_WARN_REQUIREMENTS.setVisible( not requirements_met )
        self.ui.LBL_WARN_ALREADY.setVisible( not doesnt_exist )
        self.ui.BTN_OK.setEnabled( (function is not None) and ready )
        
        self.actions.adjust_window_size()
    
    
    def query_exists( self ):
        raise NotImplementedError( "abstract" )
    
    
    def query_ready( self ):
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
                          '<html><body>You need to <a href="action:create_alignments">create the alignments</a> before creating the trees.</body></html>',
                          '<html><body>Trees already exist, you can <a href="action:view_trees">view the trees</a>, <a href="action:drop_trees">remove them</a> or proceed to <a href="action:create_fusions">finding the fusions</a>.</body></html>',
                          tree,
                          ext_generating.create_trees )


class FrmCreateAlignment( FrmRunAlgorithm ):
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
                          '<html><body>You need to <a href="action:create_components">create the components</a> before creating the alignments.</body></html>',
                          '<html><body>Alignments already exist, you can <a href="action:view_alignments">view the alignments</a>, <a href="action:drop_alignments">remove them</a> or proceed to <a href="action:create_trees">creating the trees</a>.</body></html>',
                          alignment,
                          ext_generating.create_alignments )
