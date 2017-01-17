#!/bin/bash

# This script compiles mainwindow.ui into mainwindow.py
# It is placed here to assist code development and does not need to be invoked unless you have modified the *_designer files
# Both of these files should already be present in the git repository

echo "This script compiles the resources"
python3 /usr/local/bin/pyrcc5 resources.qrc -o resources_rc.py

cd Forms

echo "This script compiles the UIs"
python3 /usr/local/bin/pyuic5 FrmMain_designer.ui -o FrmMain_designer.py

echo "And this one looks for (and prints) missing signal handlers"
python3 ../pyguisignal/pyguisignal.py FrmMain_designer.py FrmMain.py

echo "We're all done"
