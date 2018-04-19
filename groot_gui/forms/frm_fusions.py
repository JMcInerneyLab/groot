from typing import Iterable
from PyQt5.QtWidgets import QTreeWidgetItem
from intermake.visualisables.visualisable import IVisualisable
from mhelper_qt import exceptToGui, TreeHeaderMap

from groot_gui.forms.resources import resources
from groot_gui.forms.designer import frm_fusions_designer
from groot_gui.forms.frm_base import FrmBase


class FrmFusions( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_fusions_designer.Ui_Dialog( self )
        self.setWindowTitle( "Fusions" )
        
        self.headers = TreeHeaderMap( self.ui.TVW_MAIN )
        self.update_list()
    
    
    def update_list( self ):
        model = self.get_model()
        self.ui.TVW_MAIN.clear()
        
        if len( model.fusion_events ) == 0:
            self.ui.LBL_MAIN.setText( "Fusions have not yet been generated" )
            return
        
        self.ui.LBL_MAIN.setText( "Model contains {} fusion events".format( len( model.fusion_events ) ) )
        
        for fusion in model.fusion_events:
            fusion_item = QTreeWidgetItem()
            fusion_item.setIcon( self.headers["name"], fusion.visualisable_info().icon() )
            fusion_item.setText( self.headers["name"], "{}".format( fusion ) )
            fusion_item.setText( self.headers["index"], "{}".format( fusion.index ) )
            fusion_item.setText( self.headers["left"], "{}".format( fusion.component_a ) )
            fusion_item.setText( self.headers["right"], "{}".format( fusion.component_b ) )
            fusion_item.setText( self.headers["component"], "{}".format( fusion.component_c ) )
            self.__add_array_item( fusion_item, "Products", fusion.products )
            self.__add_array_item( fusion_item, "Future", fusion.future_products )
            self.ui.TVW_MAIN.addTopLevelItem( fusion_item )
            
            for formation in fusion.formations:
                formation_item = QTreeWidgetItem()
                formation_item.setIcon( self.headers["name"], resources.black_fusion.icon() )
                formation_item.setText( self.headers["name"], "{}".format( formation ) )
                formation_item.setText( self.headers["index"], "Index: {}".format( formation.index ) )
                formation_item.setText( self.headers["component"], "{}".format( formation.component ) )
                self.__add_array_item( formation_item, "Sequences", formation.sequences )
                self.__add_array_item( formation_item, "All", formation.pertinent_inner )
                fusion_item.addChild( formation_item )
                
                for point in formation.points:
                    point_item = QTreeWidgetItem()
                    point_item.setIcon( 0, resources.black_fusion.icon() )
                    point_item.setText( 0, "{}".format( point ) )
                    point_item.setText( 1, "{}".format( point.index ) )
                    point_item.setText( 2, "{}".format( point.point_component ) )
                    self.__add_array_item( point_item, "Sequences", point.outer_sequences )
                    self.__add_array_item( point_item, "All", point.pertinent_outer )
                    fusion_item.addChild( point_item )
    
    
    def __add_array_item( self, parent_item: QTreeWidgetItem, name: str, array: Iterable[object] ):
        array_item = QTreeWidgetItem()
        array_item.setText( self.headers["name"], name )
        parent_item.addChild( array_item )
        
        for element in sorted( array, key = str ):
            element_item = QTreeWidgetItem()
            
            if isinstance( element, IVisualisable ):
                element_item.setIcon( self.headers["name"], element.visualisable_info().icon.icon() )
            
            element_item.setText( self.headers["name"], str( element ) )
            array_item.addChild( element_item )
    
    
    def on_plugin_completed( self ):
        self.update_list()
