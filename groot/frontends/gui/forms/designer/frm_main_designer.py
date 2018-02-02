# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_main_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(836, 370)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.FRA_HELP = QtWidgets.QFrame(self.centralwidget)
        self.FRA_HELP.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FRA_HELP.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FRA_HELP.setObjectName("FRA_HELP")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.FRA_HELP)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.LBL_FIRST_MESSAGE = QtWidgets.QLabel(self.FRA_HELP)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_FIRST_MESSAGE.sizePolicy().hasHeightForWidth())
        self.LBL_FIRST_MESSAGE.setSizePolicy(sizePolicy)
        self.LBL_FIRST_MESSAGE.setStyleSheet("background:white;\n"
"padding:16;")
        self.LBL_FIRST_MESSAGE.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.LBL_FIRST_MESSAGE.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LBL_FIRST_MESSAGE.setObjectName("LBL_FIRST_MESSAGE")
        self.gridLayout_2.addWidget(self.LBL_FIRST_MESSAGE, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.FRA_HELP, 0, 0, 1, 1)
        self.MDI_AREA = QtWidgets.QMdiArea(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MDI_AREA.sizePolicy().hasHeightForWidth())
        self.MDI_AREA.setSizePolicy(sizePolicy)
        self.MDI_AREA.setObjectName("MDI_AREA")
        self.gridLayout.addWidget(self.MDI_AREA, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 836, 22))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.LBL_FIRST_MESSAGE.setText(_translate("MainWindow", "<html><head/><body>\n"
"<h1>Groot</h1>\n"
"<p><i>Groot version $(VERSION)</i></p>\n"
"<p>Would you like to:</p>\n"
"<ul>\n"
"<li>Grootle around yourself in the <a href=\"action:show_workflow_form\">workflow</a>.</li>\n"
"<li>Have a magical <a href=\"action:show_wizard_form\">wizard</a> do everything for you</li>\n"
"<li>Stand alone and <a href=\"action:dismiss_startup_screen\">dismiss</a> this message.</li>\n"
"<li>View the <a href=\"action:show_help\">documentation</a> online.</li>\n"
"</ul>\n"
"$(RECENT_FILES)\n"
"</body></html>"))


