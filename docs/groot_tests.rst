====================
The Groot test suite
====================

Groot comes with the ability to generate random test cases.

The test suite is packaged separately, to load it, run the following commands from within Groot:

CLI:::

    groot
    import groot_tests
    use groot_tests
    
PYS:::

    import groot
    import groot_tests

After loading the test suite, to create and run tests, use the ``create.test n`` (CLI) or ``groot_tests.create_test(n)`` (PYS) command,
where ``n`` specifies the test case identifier (representing the expected number of components).

All tests case trees should be recoverable (mutations permitting) by Groot using the default settings,
with the exclusion of the specific instances of test case 4, as noted below.

---------------------
Case 1: Single fusion
---------------------

::

     A-------->
      \     a0
       \a1
        \
         -->C--->
        /
       /b1
      /     b0
     B-------->

------------------------
Case 4: Repeated fusions
------------------------

::

     A------------------->
      \       \       a0
       \a1     \a2
        \       \
         -->C    -->D
        /       /
       /a2     /b2
      /       /       b0
     B------------------->

As the test cases are randomly generated, this may result in *a1=a2* and/or *b1=b2*, giving the *triangle* or *spaceship* problems listed below. 

----------------------
Case 5: Fusion cascade
----------------------

::
     A
      \
       -->C
      /    \
     B      -->E
           /
          D

------------------
Case 7: Fusion web
------------------

::

     A
      \
       -->C
      /    \
     B      \
             -->G
     D      /
      \    /
       -->F
      /
     E
