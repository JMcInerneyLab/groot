from typing import Iterable

import intermake_qt
import groot as gr
import mhelper_qt as qt

from groot_gui.forms.resources import resources
from groot_gui.forms.designer import frm_fusions_designer
from groot_gui.forms.frm_base import FrmBase
from mhelper_qt import exqtSlot


class FrmFusions( FrmBase ):
    """
    The fusions screen displays the list of fusions found in the current model.
    
    More details on fusions themselves can be found in the `Fusion` class documentation.
    """
    
    
    @qt.exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_fusions_designer.Ui_Dialog( self )
        self.setWindowTitle( "Fusions" )
        
        self.headers = qt.TreeHeaderMap( self.ui.TVW_MAIN )
        self.update_list()
    
    
    def update_list( self ):
        model = self.get_model()
        self.ui.TVW_MAIN.clear()
        
        if len( model.fusions ) == 0:
            self.ui.LBL_MAIN.setText( "Fusions have not yet been generated" )
            return
        
        self.ui.LBL_MAIN.setText( "Model contains {} fusion events".format( len( model.fusions ) ) )
        
        for fusion in model.fusions:
            assert isinstance( fusion, gr.Fusion )
            fusion_item = qt.QTreeWidgetItem()
            
            fusion_item.setIcon( self.headers["name"], resources.black_fusion.icon() )
            fusion_item.setText( self.headers["name"], "FUSION {}".format( fusion ) )
            self.__add_array_item( fusion_item, "in", fusion.components_in, intermake_qt.resources.list )
            fusion_item.setText( self.headers["component"], "{}".format( fusion.component_out ) )
            
            self.ui.TVW_MAIN.addTopLevelItem( fusion_item )
            
            for formation in fusion.formations:
                assert isinstance( formation, gr.Formation )
                formation_item = qt.QTreeWidgetItem()
                formation_item.setIcon( self.headers["name"], resources.black_fusion.icon() )
                formation_item.setText( self.headers["name"], "FORMATION {}".format( formation ) )
                formation_item.setText( self.headers["component"], "{}".format( formation.component ) )
                
                self.__add_array_item( formation_item, "Genes", formation.genes, intermake_qt.resources.list )
                self.__add_array_item( formation_item, "Pertinent", formation.pertinent_inner, intermake_qt.resources.list )
                fusion_item.addChild( formation_item )
                
                for point in formation.points:
                    assert isinstance( point, gr.Point )
                    
                    point_item = qt.QTreeWidgetItem()
                    point_item.setIcon( self.headers["name"], resources.black_fusion.icon() )
                    point_item.setText( self.headers["name"], "POINT {}".format( point ) )
                    point_item.setText( self.headers["component"], "{}".format( point.point_component ) )
                    
                    self.__add_array_item( point_item, "Genes", point.outer_genes, intermake_qt.resources.list )
                    self.__add_array_item( point_item, "Pertinent", point.pertinent_outer, intermake_qt.resources.list )
                    formation_item.addChild( point_item )
        
        self.ui.TVW_MAIN.expandAll()
        self.ui.TVW_MAIN.resizeColumnToContents( 0 )
    
    
    def __add_array_item( self,
                          parent_item: qt.QTreeWidgetItem,
                          name: str,
                          array: Iterable[object],
                          icon: qt.ResourceIcon ):
        array_item = qt.QTreeWidgetItem()
        array_item.setText( self.headers["name"], name )
        parent_item.addChild( array_item )
        
        for element in sorted( array, key = str ):
            item = qt.QTreeWidgetItem()
            item.setIcon( self.headers["name"], icon.icon() )
            item.setText( self.headers["name"], str( element ) )
            
            if isinstance( element, gr.Gene ):
                item.setText( self.headers["component"], str( element.model.components.find_component_for_major_gene( element ) ) )
            
            array_item.addChild( item )
    
    
    def on_command_completed( self ):
        self.update_list()
    
    
    @qt.exqtSlot()
    def on_BTN_HELP_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_my_help()
    
    @exqtSlot()
    def on_BTN_REFRESH_clicked(self) -> None:
        """
        Signal handler:
        """
        self.update_list()
