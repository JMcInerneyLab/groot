# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_fusions_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(723, 589)
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
        self.LBL_MAIN = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_MAIN.sizePolicy().hasHeightForWidth())
        self.LBL_MAIN.setSizePolicy(sizePolicy)
        self.LBL_MAIN.setObjectName("LBL_MAIN")
        self.horizontalLayout_21.addWidget(self.LBL_MAIN)
        self.verticalLayout.addWidget(self.frame)
        self.TVW_MAIN = QtWidgets.QTreeWidget(Dialog)
        self.TVW_MAIN.setObjectName("TVW_MAIN")
        self.TVW_MAIN.headerItem().setText(0, "1")
        self.TVW_MAIN.header().setVisible(False)
        self.verticalLayout.addWidget(self.TVW_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.LBL_MAIN.setText(_translate("Dialog", "TextLabel"))
        self.LBL_MAIN.setProperty("style", _translate("Dialog", "heading"))

