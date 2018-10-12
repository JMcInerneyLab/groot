=================
Groot Terminology
=================

List of terms used in Groot. 

  =============== ============================================================================================== 
  Term            Description                                                                                    
  =============== ==============================================================================================
  Fusion event    An event in the evolution in which 2 genes join                                                
  Fusion point    The realisation of a fusion event within an individual tree                                    
  Splits          The set of edges found within all trees                                                        
  Consensus       A subset of splits supported by the majority-rule consensus                                    
  NRFG            The N-rooted fusion graph                                                                       
  Fused graph     The N-rooted fusion graph without redundancies removed                                         
  Cleaned graph   The N-rooted fusion graph with redundancies removed                                            
  Genes           The input sequences [1]_                                                                           
  Domains         Part of a gene [1]_                                                                                
  Sites           The site data for the genes (FASTA)                                                            
  Edges           How the genes are connected (BLAST)                                                            
  Subgraphs       Stage of NRFG creation representing a part of the evolution free of fusions                    
  Subsets         The predecessors to the subgraphs - a set of genes free of fusion events                       
  Split           An edge of a tree represented as the left and right leaf-sets                                  
  =============== ==============================================================================================


.. [1] Data may be conventional or imputed, concrete or abstract - Groot doesn't care.
