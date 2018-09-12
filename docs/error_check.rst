============================
Groot automated NRFG checker
============================

The following codes may be returned from the NRFG checker. 
    
-----------------
Code C1. No nodes
-----------------

::

    Code C1. The NRFG is bad. It doesn't contain any nodes.

    
-----------------    
Code C2. No edges
-----------------

::

    Code C2. The NRFG is bad. It doesn't contain any edges.
    

----------------------------    
Code C3. Multiple components
----------------------------

::

    Code C3. The NRFG is bad. It contains more than one connected component. It contains {} components.
    
----------------------------
Code C4. Badly formed fusion
----------------------------

::

    Code C4. Possible badly formed fusion at node «{}». This fusion has {} input and {} outputs, instead of the expected 2 inputs and 1 output.


--------------------------
Code C5. Badly formed root
--------------------------

::

    Code C5. Possible badly formed root at node «{}». This node has {} parents instead of the expected 0.


---------------------------
Code C6. Badly formed clade
---------------------------

::

    Code C6. Possible badly formed clade at node «{}». This node has {} parents instead of the expected 1.

------------------------------
Code C7. Badly formed sequence
------------------------------

::

    Code C7. Possibly badly formed sequence at node «{}». This node has {} children instead of the expected 0.

------------------------
Code C8. Redundant clade
------------------------

::

    Code C8. Possible redundant clade at node «{}». This node has {} children instead of 2 or more.