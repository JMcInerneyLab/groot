from groot import similarity_algorithms
from mhelper import file_helper
from intermake import subprocess_helper


@similarity_algorithms.register( "blastp", default = True )
def blastp( fasta: str ) -> str:
    """
    Uses protein blast to create the similarity matrix.
    """
    file_helper.write_all_text( "fasta.fasta", fasta )
    subprocess_helper.run_subprocess( ["blastp", "-query", "fasta.fasta", "-subject", "fasta.fasta", "-outfmt", "6", "-out", "blast.blast"] )
    return file_helper.read_all_text( "blast.blast" )
