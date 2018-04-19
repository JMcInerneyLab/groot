from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtWidgets import QGraphicsScene, QGridLayout, QSizePolicy
from groot.constants import EMode, EChanges
from mhelper_qt import exceptToGui, exqtSlot

from groot import LegoUserDomain
from groot.data import global_view
from groot_gui.forms.designer import frm_lego_designer
from groot_gui.forms.frm_base import FrmSelectingToolbar
from groot_gui.forms.frm_view_options import FrmViewOptions
from groot_gui.utilities.gui_view import LegoView_Model
from groot_gui.utilities.gui_view_utils import ESelect, InteractiveGraphicsView, LegoSelection
from groot_gui.utilities import layout
from typing import Optional


class FrmLego( FrmSelectingToolbar ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_lego_designer.Ui_Dialog( self )
        self.setWindowTitle( "Lego Diagram Editor" )
        self.bind_to_label( self.ui.LBL_NO_DOMAINS )
        self.bind_to_workflow_box( self.ui.FRA_TOOLBAR, ESelect.ALL )
        
        #
        # Graphics view
        #
        v = InteractiveGraphicsView()
        self.ctrl_graphics_view: InteractiveGraphicsView = v
        sizePolicy = QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        sizePolicy.setHeightForWidth( v.sizePolicy().hasHeightForWidth() )
        v.setSizePolicy( sizePolicy )
        v.setObjectName( "graphicsView" )
        v.setBackgroundBrush( QBrush( QColor( 255, 255, 255 ) ) )
        v.setInteractive( True )
        layout = QGridLayout()
        self.ui.FRA_MAIN.setLayout( layout )
        layout.addWidget( v )
        
        # Open GL rendering
        if global_view.options().opengl:
            v.setViewport( QGLWidget( QGLFormat( QGL.SampleBuffers ) ) )
        
        # Default (empty) scene
        scene = QGraphicsScene()
        scene.addRect( QRectF( -10, -10, 20, 20 ) )
        
        v.setScene( scene )
        
        #
        # Create our model view!
        #
        self.model_view: LegoView_Model = None
        self.update_view()
    
    
    def update_view( self, changes = EChanges.MODEL_OBJECT ):
        """
        Update the view with changes from the model.
        """
        model = self.get_model()
        m = global_view.options().lego_mode
        
        self.ui.BTN_SEL_COMPONENT.setChecked( m == EMode.COMPONENT )
        self.ui.BTN_SEL_SEQUENCE.setChecked( m == EMode.SEQUENCE )
        self.ui.BTN_SEL_DOMAIN.setChecked( m == EMode.SUBSEQUENCE )
        
        # No domains warning?
        self.ui.LBL_NO_DOMAINS.setVisible( not model.user_domains )
        
        if changes.MODEL_OBJECT or changes.MODEL_ENTITIES or changes.COMPONENTS:
            if self.model_view:
                self.model_view.scene.setParent( None )
            
            self.model_view = LegoView_Model( self, self.ctrl_graphics_view, self.get_model() )
            self.ctrl_graphics_view.setScene( self.model_view.scene )
    
    
    def handle_domain_clicked( self, domain_clicked: Optional[LegoUserDomain], toggle: bool ) -> None:
        """
        User has clicked on a domain in the view.
        We now need to add the domain to the current selection.
         
        :param domain_clicked:      Domain clicked 
        :param toggle:              When true, we toggle the domain's selected status, rather than making it the sole selection.
        """
        if domain_clicked is None:
            self.actions.set_selection( LegoSelection() )
            self.model_view.user_move_enabled = False
            self.model_view.scene.update()
            return
        
        model = self.get_model()
        o = global_view.options()
        
        select = set()
        
        if o.lego_mode == EMode.COMPONENT:
            component = model.components.find_component_for_major_sequence( domain_clicked.sequence )
            
            for domain in model.user_domains:
                if any( domain.has_overlap( d2 ) for d2 in component.minor_subsequences ):
                    select.add( domain )
        elif o.lego_mode == EMode.SUBSEQUENCE:
            select.add( domain_clicked )
        elif o.lego_mode == EMode.SEQUENCE:
            for domain in model.user_domains:
                if domain.sequence == domain_clicked.sequence:
                    select.add( domain )
        
        if toggle:
            # Base whether to select or deselect on the domain clicked
            # (don't just toggle everything, that's annoying to the user)
            selection = self.get_selection()
            
            if domain_clicked in selection:
                # Deactivate
                select = selection.items - select
                self.actions.set_selection( LegoSelection( select ) )
            else:
                # Activate
                select = selection.items.union( select )
        else:
            self.model_view.user_move_enabled = False
        
        self.actions.set_selection( LegoSelection( frozenset( select ) ) )
        self.model_view.scene.update()
    
    
    def on_selection_changed( self ):
        """
        FrmBase selection has changed (this just highlights elements and is not the same as the selection in the window).
        """
        pass
    
    
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
    def on_BTN_MOVE_clicked( self ) -> None:
        """
        Signal handler:
        """
        model = self.get_model()
        o = model.ui_options
        o.move_enabled = self.ui.BTN_MOVE.isChecked()
        self.model_view.scene.update()
    
    
    @exqtSlot()
    def on_BTN_SEL_COMPONENT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.refresh_view()
    
    
    @exqtSlot()
    def on_BTN_SEL_SEQUENCE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.refresh_view()
    
    
    @exqtSlot()
    def on_BTN_SEL_DOMAIN_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.refresh_view()
    
    
    @exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.update_view()
    
    
    def on_plugin_completed( self ):
        self.update_view( self.actions.frm_main.completed_changes )
    
    
    def refresh_view( self ):
        o = global_view.options()
        
        if self.ui.BTN_SEL_COMPONENT.isChecked():
            o.lego_mode = EMode.COMPONENT
        elif self.ui.BTN_SEL_DOMAIN.isChecked():
            o.lego_mode = EMode.SUBSEQUENCE
        elif self.ui.BTN_SEL_SEQUENCE.isChecked():
            o.lego_mode = EMode.SEQUENCE
        
        self.ctrl_graphics_view.update()
