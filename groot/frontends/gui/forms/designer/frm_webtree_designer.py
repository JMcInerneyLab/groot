# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_webtree_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1150, 842)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_21.setSpacing(0)
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.BTN_SELECTION = QtWidgets.QToolButton(self.frame)
        self.BTN_SELECTION.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.BTN_SELECTION.setArrowType(QtCore.Qt.DownArrow)
        self.BTN_SELECTION.setObjectName("BTN_SELECTION")
        self.horizontalLayout_21.addWidget(self.BTN_SELECTION)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_21.addItem(spacerItem)
        self.verticalLayout.addWidget(self.frame)
        self.WIDGET_OPEN = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.WIDGET_OPEN.sizePolicy().hasHeightForWidth())
        self.WIDGET_OPEN.setSizePolicy(sizePolicy)
        self.WIDGET_OPEN.setObjectName("WIDGET_OPEN")
        self.gridLayout = QtWidgets.QGridLayout(self.WIDGET_OPEN)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)
        self.BTN_SYSTEM_BROWSER = QtWidgets.QPushButton(self.WIDGET_OPEN)
        self.BTN_SYSTEM_BROWSER.setObjectName("BTN_SYSTEM_BROWSER")
        self.gridLayout.addWidget(self.BTN_SYSTEM_BROWSER, 0, 0, 1, 1)
        self.BTN_BROWSE_HERE = QtWidgets.QPushButton(self.WIDGET_OPEN)
        self.BTN_BROWSE_HERE.setObjectName("BTN_BROWSE_HERE")
        self.gridLayout.addWidget(self.BTN_BROWSE_HERE, 1, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.WIDGET_OPEN)
        self.WIDGET_MAIN = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.WIDGET_MAIN.sizePolicy().hasHeightForWidth())
        self.WIDGET_MAIN.setSizePolicy(sizePolicy)
        self.WIDGET_MAIN.setObjectName("WIDGET_MAIN")
        self.verticalLayout.addWidget(self.WIDGET_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.BTN_SELECTION.setText(_translate("Dialog", "Selection"))
        self.BTN_SYSTEM_BROWSER.setText(_translate("Dialog", "Show in system browser"))
        self.BTN_BROWSE_HERE.setText(_translate("Dialog", "Show in this window"))

