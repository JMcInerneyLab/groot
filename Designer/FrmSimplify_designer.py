# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\MJR\Apps\legodiagram\Designer\FrmSimplify_designer.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.NUM_TOLERANCE = QtWidgets.QSpinBox(Dialog)
        self.NUM_TOLERANCE.setAccelerated(True)
        self.NUM_TOLERANCE.setObjectName("NUM_TOLERANCE")
        self.verticalLayout.addWidget(self.NUM_TOLERANCE)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.BTNBOX_MAIN = QtWidgets.QDialogButtonBox(Dialog)
        self.BTNBOX_MAIN.setOrientation(QtCore.Qt.Horizontal)
        self.BTNBOX_MAIN.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BTNBOX_MAIN.setObjectName("BTNBOX_MAIN")
        self.verticalLayout.addWidget(self.BTNBOX_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setStatusTip(_translate("Dialog", "How close two points in a sequence must be to be considered the same."))
        self.label.setWhatsThis(_translate("Dialog", "<html><head/><body><p>How close two points in a sequence must be to be considered the same.</p><p>Points are merged using HCA. Sequence starts are always drawn from the lowest of the set of merged points, whilst sequence ends are always drawn from the highest.</p></body></html>"))
        self.label.setText(_translate("Dialog", "Tolerance"))
        self.NUM_TOLERANCE.setStatusTip(_translate("Dialog", "How close two points in a sequence must be to be considered the same."))
        self.NUM_TOLERANCE.setWhatsThis(_translate("Dialog", "<html><head/><body><p>How close two points in a sequence must be to be considered the same.</p><p>Points are merged using HCA. Sequence starts are always drawn from the lowest of the set of merged points, whilst sequence ends are always drawn from the highest.</p></body></html>"))

