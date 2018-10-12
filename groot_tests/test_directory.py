from os import path
import intermake
from mhelper import file_helper


class TestDirectory:
    def __init__( self, name ):
        if name is None:
            name = self.get_unused_name()
        
        if path.sep in name:
            raise ValueError( "Invalid test name." )
        
        self.t_name = name
        self.t_folder = path.join( TestDirectory.get_test_folder(), name )
        self.r_folder = path.join( TestDirectory.get_results_folder(), name )
        
        self.t_tree = path.join( self.t_folder, "tree.tsv" )
        self.t_ini = path.join( self.t_folder, "groot.ini" )
        
        self.r_comparison = path.join( self.r_folder, "comparison_report.html" )
        self.r_summary = path.join( self.r_folder, "test_summary.ini" )
        self.r_model = path.join( self.r_folder, "session.groot" )
        self.r_alignments = path.join( self.r_folder, "alignments.fasta" )
        self.rc_ini = path.join( self.r_folder, "input_groot.ini" )
    
    @staticmethod
    def get_test_folder():
        return intermake.Controller.ACTIVE.app.local_data.local_folder( "test_cases" )
    

    @staticmethod
    def get_results_folder():
        return intermake.Controller.ACTIVE.app.local_data.local_folder( "test_cases_results" )


    @staticmethod
    def get_unused_name():
        path_ = file_helper.incremental_name( path.join( TestDirectory.get_test_folder(), "test" ) )
        return file_helper.get_file_name( path_ )
