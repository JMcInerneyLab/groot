# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_about_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(808, 1117)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.LBL_MAIN = QtWidgets.QLabel(Dialog)
        self.LBL_MAIN.setStyleSheet("margin: 32px;")
        self.LBL_MAIN.setObjectName("LBL_MAIN")
        self.gridLayout.addWidget(self.LBL_MAIN, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.LBL_MAIN.setText(_translate("Dialog", "<h1>About Groot</h1>\n"
"<b>Groot is free software.</b>\n"
"\n"
"<h2>Acknowledgements</h2>\n"
"<table cellpadding=\"16\">\n"
"  <tr>\n"
"    <td><img width=\"128\" source=\":/manchester_logo.png\"/></td>\n"
"    <td><img width=\"128\" source=\":/bbsrc_logo.png\"/></td> \n"
"  </tr>\n"
"<tr>\n"
"    <td>The University Of Manchester</td>\n"
"    <td>BBSRC</td> \n"
"  </tr>\n"
"</table>\n"
"\n"
"<h2>Groot</h2>\n"
"Groot is copyright (c) Martin Rusilowicz\n"
"<ul>\n"
"<li>Version: $(GROOT)</li>\n"
"<li>Webpage: www.bitbucket.org/mjr129/groot</li>\n"
"<li>License: https://www.gnu.org/licenses/agpl-3.0.html</li>\n"
"</ul><br/>\n"
"<img width=\"96\" source=\":/groot_logo.png\"/>\n"
"\n"
"<h2>Intermake</h2>\n"
"Intermake is copyright (c) Martin Rusilowicz\n"
"<ul>\n"
"<li>Version $(INTERMAKE)</li>\n"
"<li>Webpage: www.bitbucket.org/mjr129/intermake</li>\n"
"<li>License: https://www.gnu.org/licenses/agpl-3.0.html</li>\n"
"</ul><br/>\n"
"<img width=\"96\" source=\":/intermake_logo.png\"/>\n"
"\n"
"<h2>Qt5</h2>\n"
"Qt is copyright (c) The Qt Company\n"
"<ul>\n"
"<li>Version: $(QT)\n"
"<li>Webpage: https://www.qt.io/</li>\n"
"</ul><br/>\n"
"<img width=\"96\" source=\":/qt_logo.png\"/>\n"
"\n"
"<h2>PyQt5</h2>\n"
"PyQt5 is copyright (c) Riverbank Computing Limited\n"
"<ul>\n"
"<li>Version: $(PYQT)\n"
"<li>Webpage: https://www.riverbankcomputing.com/software/pyqt/.</li>\n"
"</ul>\n"
"\n"
"<h2>Images</h2>\n"
"Images made by Freepik, Google and Good Ware from www.flaticon.com\n"
"<ul>\n"
"<li>Webpage: https://www.flaticon.com</li>\n"
"</ul>\n"
"\n"
"\n"
""))


