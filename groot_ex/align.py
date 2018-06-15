from groot import Model, alignment_algorithms
from mhelper import file_helper, ignore
from intermake import subprocess_helper


@alignment_algorithms.register( "muscle" )
def align_muscle( model: Model, fasta: str ) -> str:
    """
    Uses MUSCLE to align.
    """
    ignore( model )
    
    file_helper.write_all_text( "in_file.fasta", fasta )
    
    subprocess_helper.run_subprocess( "muscle -in in_file.fasta -out out_file.fasta".split( " " ) )
    
    return file_helper.read_all_text( "out_file.fasta" )


@alignment_algorithms.register( "as_is" )
def align_as_is( model: Model, fasta: str ) -> str:
    """
    Uses the FASTA as it already is.
    """
    ignore( model )
    return fasta
