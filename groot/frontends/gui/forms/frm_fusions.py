from PyQt5.QtWidgets import QTreeWidgetItem

from groot.data import global_view
from groot.frontends.gui.forms.designer import frm_fusions_designer

from groot.frontends.gui.forms.frm_alignment import FrmAlignment
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.forms.frm_big_text import FrmBigText
from groot.frontends.gui.forms.frm_lego import FrmLego
from groot.frontends.gui.forms.frm_samples import FrmSamples
from groot.frontends.gui.forms.frm_selection_list import FrmSelectionList
from groot.frontends.gui.forms.frm_webtree import FrmWebtree
from groot.frontends.gui.gui_view_utils import EChanges
from mhelper import string_helper
from mhelper_qt import exqtSlot, exceptToGui
from groot import extensions


class FrmFusions( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_fusions_designer.Ui_Dialog( self )
        self.setWindowTitle( "Fusions" )
        self.update_list()
    
    
    def update_list( self ):
        model = self.get_model()
        self.ui.TVW_MAIN.clear()
        
        if len( model.fusion_events ) == 0:
            self.ui.LBL_MAIN.setText( "Fusions have not yet been generated" )
            return
        
        self.ui.LBL_MAIN.setText( "Model contains {} fusion events".format( len( model.fusion_events ) ) )
        
        for fusion in model.fusion_events:
            item1 = QTreeWidgetItem()
            item1.setText( 0, str( fusion ) )
            item1.tag = fusion
            self.ui.TVW_MAIN.addTopLevelItem( item1 )
            
            for index, point in enumerate( fusion.points ):
                item2 = QTreeWidgetItem()
                item2.setText( 0, str( point.component ) )
                
                item3 = QTreeWidgetItem()
                item3.setText( 0, string_helper.format_array( point.pertinent_inner ) )
                item2.addChild( item3 )
                
                item3 = QTreeWidgetItem()
                item3.setText( 0, string_helper.format_array( point.pertinent_outer ) )
                item2.addChild( item3 )
                
                item1.tag = point
                item1.addChild( item2 )
    
    
    def on_fusions_changed( self ):
        self.update_list()
