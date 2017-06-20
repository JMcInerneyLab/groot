# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './Designer/FrmTreeSelector_designer.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(822, 670)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.LST_TYPE = QtWidgets.QComboBox(self.groupBox)
        self.LST_TYPE.setObjectName("LST_TYPE")
        self.verticalLayout_2.addWidget(self.LST_TYPE)
        self.horizontalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LST_ROOT = QtWidgets.QComboBox(self.groupBox_2)
        self.LST_ROOT.setObjectName("LST_ROOT")
        self.verticalLayout.addWidget(self.LST_ROOT)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.BTNBOX_MAIN = QtWidgets.QDialogButtonBox(Dialog)
        self.BTNBOX_MAIN.setOrientation(QtCore.Qt.Horizontal)
        self.BTNBOX_MAIN.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BTNBOX_MAIN.setObjectName("BTNBOX_MAIN")
        self.verticalLayout_3.addWidget(self.BTNBOX_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "Type"))
        self.groupBox_2.setTitle(_translate("Dialog", "Root"))

