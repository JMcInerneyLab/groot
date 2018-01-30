# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_samples_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(802, 630)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.FRA_RECENT_2 = QtWidgets.QGroupBox(Dialog)
        self.FRA_RECENT_2.setObjectName("FRA_RECENT_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.FRA_RECENT_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.BTN_BROWSE = QtWidgets.QPushButton(self.FRA_RECENT_2)
        self.BTN_BROWSE.setObjectName("BTN_BROWSE")
        self.verticalLayout_2.addWidget(self.BTN_BROWSE)
        self.verticalLayout.addWidget(self.FRA_RECENT_2)
        self.FRA_RECENT = QtWidgets.QGroupBox(Dialog)
        self.FRA_RECENT.setObjectName("FRA_RECENT")
        self.verticalLayout.addWidget(self.FRA_RECENT)
        self.FRA_SAMPLES = QtWidgets.QGroupBox(Dialog)
        self.FRA_SAMPLES.setObjectName("FRA_SAMPLES")
        self.verticalLayout.addWidget(self.FRA_SAMPLES)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.FRA_RECENT_2.setTitle(_translate("Dialog", "File system"))
        self.BTN_BROWSE.setText(_translate("Dialog", "Browse"))
        self.FRA_RECENT.setTitle(_translate("Dialog", "Recent"))
        self.FRA_SAMPLES.setTitle(_translate("Dialog", "Samples"))

