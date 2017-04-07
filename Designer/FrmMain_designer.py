# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\MJR\Apps\legodiagram\Designer\FrmMain_designer.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(868, 575)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 868, 21))
        self.menuBar.setObjectName("menuBar")
        self.menu_File = QtWidgets.QMenu(self.menuBar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Edit = QtWidgets.QMenu(self.menuBar)
        self.menu_Edit.setObjectName("menu_Edit")
        self.menu_View = QtWidgets.QMenu(self.menuBar)
        self.menu_View.setObjectName("menu_View")
        MainWindow.setMenuBar(self.menuBar)
        self.action_New = QtWidgets.QAction(MainWindow)
        self.action_New.setObjectName("action_New")
        self.action_Import = QtWidgets.QAction(MainWindow)
        self.action_Import.setObjectName("action_Import")
        self.action_Exit = QtWidgets.QAction(MainWindow)
        self.action_Exit.setObjectName("action_Exit")
        self.action_Preferences = QtWidgets.QAction(MainWindow)
        self.action_Preferences.setObjectName("action_Preferences")
        self.action_Simplify_layout = QtWidgets.QAction(MainWindow)
        self.action_Simplify_layout.setObjectName("action_Simplify_layout")
        self.menu_File.addAction(self.action_New)
        self.menu_File.addAction(self.action_Import)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Exit)
        self.menu_Edit.addAction(self.action_Simplify_layout)
        self.menu_View.addAction(self.action_Preferences)
        self.menuBar.addAction(self.menu_File.menuAction())
        self.menuBar.addAction(self.menu_Edit.menuAction())
        self.menuBar.addAction(self.menu_View.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.graphicsView.setWhatsThis(_translate("MainWindow", "The plot is shown in this area"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Edit.setTitle(_translate("MainWindow", "&Edit"))
        self.menu_View.setTitle(_translate("MainWindow", "&View"))
        self.action_New.setText(_translate("MainWindow", "&New"))
        self.action_Import.setText(_translate("MainWindow", "&Import"))
        self.action_Exit.setText(_translate("MainWindow", "E&xit"))
        self.action_Preferences.setText(_translate("MainWindow", "&Preferences"))
        self.action_Simplify_layout.setText(_translate("MainWindow", "&Simplify layout"))

