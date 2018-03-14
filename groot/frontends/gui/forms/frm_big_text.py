from collections import defaultdict
import itertools
from typing import Dict, Tuple
from mgraph import exporting
from mhelper import file_helper, array_helper, string_helper
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper
from groot.frontends.gui.forms.designer import frm_big_text_designer
from groot.data.lego_model import IHasFasta, ILegoVisualisable, INamedGraph, LegoComponent
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui import gui_workflow


class FrmBigText( FrmBase ):
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_big_text_designer.Ui_Dialog( self )
        self.setWindowTitle( "Report generator" )
        
        self.html: str = ""
        
        self.ANSI_SCHEME = qt_gui_helper.ansi_scheme_light( family = 'Consolas,"Courier New",monospace' )
        self.ui.CHK_DATA.setChecked( True )
        self.ui.CHK_COLOURS.setChecked( True )
        
        self.bind_to_select( self.ui.BTN_SELECTION )
        self.bind_to_workflow_box( self.ui.GRP_WORKFLOW,
                                   self.ui.BTN_WORKFLOW,
                                   self.ui.BTN_CREATE,
                                   self.ui.BTN_REMOVE,
                                   self.ui.BTN_VIEW,
                                   gui_workflow.VISUALISERS.VIEW_TEXT,
                                   gui_workflow.STAGES.FASTA_2 )
        
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        selection = self.get_selection()
        model = self.get_model()
        
        self.ui.BTN_SELECTION.setText( str( self.get_selection() ) )
        
        text = []
        title = self.__get_title()
        
        h = False
        
        anchors: Dict[Tuple[str, str], int] = defaultdict( lambda: len( anchors ) )
        
        for item in selection:
            if isinstance( item, ILegoVisualisable ):
                name = str( item )
                text.append( '<a name="{}" /><h2>{}</h2>'.format( anchors[(name, "")], name ) )
                
                #
                # Trees and graphs
                #
                if isinstance( item, INamedGraph ) and item.graph is not None and self.ui.CHK_GRAPHS.isChecked():
                    if len( list( item.graph.nodes.roots ) ) == 1:
                        text.append( '<a name="{}" />'.format( anchors[(name, "Tree")] ) )
                        text.append( "<h3>Tree</h3>" )
                        text.append( "<p>" + exporting.export_newick( item.graph ) + "</p>" )
                    else:
                        text.append( '<a name="{}" />'.format( anchors[(name, "Graph")] ) )
                        text.append( "<h3>Graph</h3>" )
                        text.append( "<p>" + exporting.export_compact( item.graph ) + "</p>" )
                
                #
                # ALIGNMENT
                #
                if isinstance( item, LegoComponent ) and item.alignment and self.ui.CHK_ALIGNMENTS.isChecked():
                    text.append( '<a name="{}" />'.format( anchors[(name, "Alignment")] ) )
                    text.append( "<h3>Alignment</h3>" )
                    text.append( self.__get_fasta( item.alignment, model ) )
                
                #
                # FASTA
                #
                if isinstance( item, IHasFasta ) and self.ui.CHK_FASTA.isChecked():
                    text.append( '<a name="{}" />'.format( anchors[(name, "FASTA")] ) )
                    if isinstance( item, LegoComponent ):
                        text.append( "<h3>FASTA (unaligned)</h3>" )
                    else:
                        text.append( "<h3>FASTA</h3>" )
                    text.append( self.__get_fasta( item.to_fasta(), model ) )
                
                #
                # Data table
                #
                if self.ui.CHK_DATA.isChecked():
                    text.append( "<h3>Data table</h3>" )
                    text.append( '<a name="{}" />'.format( anchors[(name, "Data")] ) )
                    vi = item.visualisable_info()
                    
                    text.append( "<table>" )
                    for i, x in enumerate( vi.iter_children() ):
                        text.append( "<tr>" )
                        if self.ui.CHK_COLOURS.isChecked():
                            text.append( '<td style="background:#E0E0E0">' )
                        else:
                            text.append( "<td>" )
                        text.append( str( x.key ) )
                        text.append( "</td>" )
                        text.append( '<td style="background:{}">'.format( "#E0FFE0" if (i % 2 == 0) else "#D0FFD0" ) )
                        v = x.get_raw_value()
                        if array_helper.is_simple_iterable( v ):
                            textx = string_helper.format_array( v )
                        else:
                            textx = str( v )
                            
                        text.append( textx.replace( "\n", "<br/>" ) )
                        text.append( "</td>" )
                        text.append( "</tr>" )
                    text.append( "</table>" )
                
                h = False
            else:
                if self.ui.CHK_MISCELLANEOUS.isChecked():
                    if not h:
                        text.append( "<h2>Other items</h2>".format( item ) )
                        h = True
                    
                    name = str( item )
                    text.append( '<a name="{}" />'.format( anchors[(name, "")] ) )
                    text.append( "{}<br/>".format( name ).replace( "\n", "<br/>" ) )
        
        toc = []
        toc.append( "<h1>{} - {}</h1>".format( title, selection ) )
        toc.append( "<h2>Table of contents</h2>" )
        
        for (i, s), v in sorted( anchors.items(), key = lambda x: x[0] ):
            if s:
                toc.append( '&nbsp;- <a href="#{}">{}</a><br/>'.format( v, s ) )
            else:
                toc.append( '<a href="#{}">{}</a><br/>'.format( v, i ) )
        
        self.html = "".join( itertools.chain( toc, text ) )
        self.ui.TXT_MAIN.setHtml( self.html )
    
    
    def __get_title( self ):
        if self.workflow == gui_workflow.STAGES.BLAST_1:
            title = "Edge data"
        elif self.workflow == gui_workflow.STAGES.FASTA_2:
            title = "Site data"
        elif self.workflow == gui_workflow.STAGES.COMPONENTS_3:
            title = "Component data"
        elif self.workflow == gui_workflow.STAGES.DOMAINS_4:
            title = "Domain data"
        elif self.workflow == gui_workflow.STAGES.ALIGNMENTS_5:
            title = "Alignment data"
        elif self.workflow == gui_workflow.STAGES.TREES_6:
            title = "Tree data"
        elif self.workflow == gui_workflow.STAGES.FUSIONS_7:
            title = "Fusion data"
        elif self.workflow == gui_workflow.STAGES.SPLITS_8:
            title = "Split data"
        elif self.workflow == gui_workflow.STAGES.CONSENSUS_9:
            title = "Consensus data"
        elif self.workflow == gui_workflow.STAGES.SUBSETS_10:
            title = "Subset data"
        elif self.workflow == gui_workflow.STAGES.SUBGRAPHS_11:
            title = "Subgraph data"
        elif self.workflow == gui_workflow.STAGES.FUSED_12:
            title = "Raw NRFG graph data"
        elif self.workflow == gui_workflow.STAGES.CLEANED_13:
            title = "Final NRFG graph data"
        elif self.workflow == gui_workflow.STAGES.CHECKED_14:
            title = "Final NRFG analysis data"
        else:
            title = "No mode selected"
        return title
    
    
    @exqtSlot()
    def __get_fasta( self, fasta, model ):
        if self.ui.CHK_COLOURS.isChecked():
            return qt_gui_helper.ansi_to_html( cli_view_utils.colour_fasta_ansi( fasta, model.site_type ), self.ANSI_SCHEME )
        else:
            return "<p>{}</p>".format( fasta )
    
    
    def on_BTN_SELECTION_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass  # intentional
    
    
    @exqtSlot()
    def on_BTN_SAVE_clicked( self ) -> None:
        """
        Signal handler:
        """
        file_name: str = qt_gui_helper.browse_save( self, "HTML (*.html);;Plain text (*.txt)" )
        
        if file_name:
            if file_name.endswith( ".txt" ):
                file_helper.write_all_text( file_name, self.ui.TXT_MAIN.toPlainText() )
            else:
                file_helper.write_all_text( file_name, self.html )
    
    
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.on_refresh_data()
    
    
    @exqtSlot()
    def on_BTN_WORKFLOW_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_REMOVE_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
