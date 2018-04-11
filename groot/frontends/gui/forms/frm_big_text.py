import itertools
from collections import defaultdict
from typing import Dict, Tuple

from intermake import visualisable
from groot.frontends.gui.forms.designer import frm_big_text_designer

from groot.data.lego_model import IHasFasta, INamedGraph, LegoComponent
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.forms.frm_base import FrmSelectingToolbar
from groot.frontends.gui.gui_view_utils import ESelect
from intermake.visualisables.visualisable import VisualisablePath
from mgraph import exporting
from mhelper import array_helper, file_helper, string_helper
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper


class FrmBigText( FrmSelectingToolbar ):
    
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
        
        self.bind_to_workflow_box( self.ui.FRA_TOOLBAR, ESelect.ALL )
        
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        selection = self.get_selection()
        model = self.get_model()
        
        text = []
        
        anchors: Dict[Tuple[str, str], int] = defaultdict( lambda: len( anchors ) )
        
        for item in selection:
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
                vi = VisualisablePath.from_visualisable_temporary( item ).info()
                
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
                        text2 = string_helper.format_array( v )
                    else:
                        text2 = str( v )
                    
                    text.append( text2.replace( "\n", "<br/>" ) )
                    text.append( "</td>" )
                    text.append( "</tr>" )
                text.append( "</table>" )
            
            if self.ui.CHK_MISCELLANEOUS.isChecked():
                text.append( "<h2>Other items</h2>".format( item ) )
                name = str( item )
                text.append( '<a name="{}" />'.format( anchors[(name, "")] ) )
                text.append( "{}<br/>".format( name ).replace( "\n", "<br/>" ) )
        
        toc = []
        toc.append( "<h1>{}</h1>".format( selection ) )
        toc.append( "<h2>Table of contents</h2>" )
        
        for (i, s), v in sorted( anchors.items(), key = lambda x: x[0] ):
            if s:
                toc.append( '&nbsp;- <a href="#{}">{}</a><br/>'.format( v, s ) )
            else:
                toc.append( '<a href="#{}">{}</a><br/>'.format( v, i ) )
        
        self.html = "".join( itertools.chain( toc, text ) )
        self.ui.TXT_MAIN.setHtml( self.html )
    
    
    @exqtSlot()
    def __get_fasta( self, fasta, model ):
        if self.ui.CHK_COLOURS.isChecked():
            return qt_gui_helper.ansi_to_html( cli_view_utils.colour_fasta_ansi( fasta, model.site_type ), self.ANSI_SCHEME )
        else:
            return "<p>{}</p>".format( fasta )
    
    
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
