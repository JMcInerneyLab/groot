from typing import Any, cast

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtWidgets import QGraphicsScene, QGridLayout, QSizePolicy
from groot.frontends.gui.forms.designer import frm_lego_designer

from groot.algorithms import layout
from groot.data.lego_model import LegoUserDomain
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.forms.frm_view_options import FrmViewOptions
from groot.frontends.gui.gui_view import LegoView_Model
from groot.frontends.gui.gui_view_utils import EChanges, LegoSelection, MyView
from mhelper_qt import exceptToGui, exqtSlot


class FrmLego( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_lego_designer.Ui_Dialog( self )
        self.setWindowTitle( "Lego Diagram Editor" )
        
        # Graphics view
        self.ui.graphicsView = MyView()
        sizePolicy = QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        sizePolicy.setHeightForWidth( self.ui.graphicsView.sizePolicy().hasHeightForWidth() )
        self.ui.graphicsView.setSizePolicy( sizePolicy )
        self.ui.graphicsView.setObjectName( "graphicsView" )
        self.ui.graphicsView.setBackgroundBrush( QBrush( QColor( 255, 255, 255 ) ) )
        
        layout = QGridLayout()
        self.ui.FRA_MAIN.setLayout( layout )
        layout.addWidget( self.ui.graphicsView )
        
        # Open GL rendering
        self.ui.graphicsView.setViewport( QGLWidget( QGLFormat( QGL.SampleBuffers ) ) )
        
        # Default (empty) scene
        scene = QGraphicsScene()
        scene.addRect( QRectF( -10, -10, 20, 20 ) )
        self.ui.graphicsView.setInteractive( True )
        self.ui.graphicsView.setScene( scene )
        
        self.model_view: LegoView_Model = None
        self.update_view()
        self.actions.bind_to_label(self.ui.LBL_NO_DOMAINS)
        self.actions.bind_to_select(self.ui.BTN_CHANGE_SELECTION)
    
    
    
    def on_plugin_completed( self, changes: EChanges ):
        self.update_view( changes )
    
    
    def update_view( self, changes = EChanges.MODEL_OBJECT ):
        model = self.get_model()
        self.ui.LBL_NO_DOMAINS.setVisible( not model.user_domains )
        view: MyView = cast( Any, self.ui ).graphicsView
        print( "updating to " + str( changes ) )
        
        if changes.MODEL_OBJECT or changes.MODEL_ENTITIES or changes.COMPONENTS:
            # The model or its contents have changed
            # - Create and apply a view for the model
            if self.model_view:
                self.model_view.scene.setParent( None )
            
            self.model_view = LegoView_Model( self, view, self.get_model() )
            view.setScene( self.model_view.scene )
    
    
    def on_selection_changed( self ):
        selection = self.get_selection()
        self.ui.BTN_CHANGE_SELECTION.setText( str( selection ) )
        
        pass  # TODO
    
    
    def commit_selection( self, domain: LegoUserDomain, toggle: bool ):
        model = self.get_model()
        
        select = set()
        
        if self.ui.RAD_SEL_COMPONENT.isChecked():
            sequence = domain.sequence
            for component in model.components:
                if sequence in component.major_sequences:
                    select.add( component )
        elif self.ui.RAD_SEL_DOMAINS.isChecked():
            select.add( domain )
        elif self.ui.RAD_SEL_GENES.isChecked():
            select.add( domain.sequence )
        
        if toggle:
            selection = self.get_selection()
            select = selection.items.union( select ) - selection.items.intersection( select )
            self.set_selection( LegoSelection( select ) )
        else:
            self.set_selection( LegoSelection( frozenset( select ) ) )
    
    
    @exqtSlot()
    def on_BTN_ALIGN_clicked( self ) -> None:
        """
        Signal handler:
        """
        OPTION_1 = "Align by domain"
        OPTION_2 = "Align subsequences"
        OPTION_3 = "Align first subsequences"
        
        choice = self.show_menu( OPTION_1, OPTION_2, OPTION_3 )
        
        selected_userdomain_views = [view for view in self.model_view.userdomain_views.values() if view.is_in_global_selection()]
        
        if choice == OPTION_1:
            for userdomain_view in selected_userdomain_views:
                layout.align_about_domain( userdomain_view )
        elif choice == OPTION_2:
            for userdomain_view in selected_userdomain_views:
                layout.align_about( userdomain_view )
        elif choice == OPTION_3:
            userdomain_views = selected_userdomain_views
            
            leftmost = min( x.pos().x() for x in userdomain_views )
            
            for userdomain_view in userdomain_views:
                userdomain_view.setX( leftmost )
                userdomain_view.save_state()
    
    
    @exqtSlot()
    def on_BTN_OPTIONS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmViewOptions )
    
            
    @exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.update_view()
    
    
    @exqtSlot()
    def on_BTN_CHANGE_SELECTION_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
