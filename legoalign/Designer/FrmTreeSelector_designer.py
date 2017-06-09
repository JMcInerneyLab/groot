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
        self.RAD_TYPE_REGULAR = QtWidgets.QRadioButton(self.groupBox)
        self.RAD_TYPE_REGULAR.setObjectName("RAD_TYPE_REGULAR")
        self.verticalLayout_2.addWidget(self.RAD_TYPE_REGULAR)
        self.RAD_TYPE_FUSED = QtWidgets.QRadioButton(self.groupBox)
        self.RAD_TYPE_FUSED.setObjectName("RAD_TYPE_FUSED")
        self.verticalLayout_2.addWidget(self.RAD_TYPE_FUSED)
        self.horizontalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.RAD_PLOT_UNROOTED = QtWidgets.QRadioButton(self.groupBox_2)
        self.RAD_PLOT_UNROOTED.setObjectName("RAD_PLOT_UNROOTED")
        self.verticalLayout.addWidget(self.RAD_PLOT_UNROOTED)
        self.RAD_PLOT_ROOTED = QtWidgets.QRadioButton(self.groupBox_2)
        self.RAD_PLOT_ROOTED.setObjectName("RAD_PLOT_ROOTED")
        self.verticalLayout.addWidget(self.RAD_PLOT_ROOTED)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.RAD_FUSEON_ROOT = QtWidgets.QRadioButton(self.groupBox_3)
        self.RAD_FUSEON_ROOT.setObjectName("RAD_FUSEON_ROOT")
        self.verticalLayout_4.addWidget(self.RAD_FUSEON_ROOT)
        self.RAD_FUSEON_ANY = QtWidgets.QRadioButton(self.groupBox_3)
        self.RAD_FUSEON_ANY.setObjectName("RAD_FUSEON_ANY")
        self.verticalLayout_4.addWidget(self.RAD_FUSEON_ANY)
        self.horizontalLayout.addWidget(self.groupBox_3)
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
        self.RAD_TYPE_REGULAR.setToolTip(_translate("Dialog", "Draw regular trees, one for each component with a tree"))
        self.RAD_TYPE_REGULAR.setText(_translate("Dialog", "Regular"))
        self.RAD_TYPE_FUSED.setToolTip(_translate("Dialog", "<html><head/><body><p>Draw trees, one for each component, and produce a fusion graph from them.</p></body></html>"))
        self.RAD_TYPE_FUSED.setText(_translate("Dialog", "Fused"))
        self.groupBox_2.setTitle(_translate("Dialog", "Plot"))
        self.RAD_PLOT_UNROOTED.setToolTip(_translate("Dialog", "<html><head/><body><p>Don\'t root the trees.</p></body></html>"))
        self.RAD_PLOT_UNROOTED.setText(_translate("Dialog", "Unrooted"))
        self.RAD_PLOT_ROOTED.setToolTip(_translate("Dialog", "<html><head/><body><p>Root the trees on the sequences you have marked as roots on the main screen.</p><p>If you haven\'t marked any, the plot will be unrooted.</p></body></html>"))
        self.RAD_PLOT_ROOTED.setText(_translate("Dialog", "Rooted"))
        self.groupBox_3.setTitle(_translate("Dialog", "Fuse on"))
        self.RAD_FUSEON_ROOT.setToolTip(_translate("Dialog", "<html><head/><body><p>Give preference to sequences marked as roots when calculating the merge point.</p></body></html>"))
        self.RAD_FUSEON_ROOT.setText(_translate("Dialog", "Root"))
        self.RAD_FUSEON_ANY.setToolTip(_translate("Dialog", "<html><head/><body><p>Don\'t give preference to any sequence when calculating the merge point.</p></body></html>"))
        self.RAD_FUSEON_ANY.setText(_translate("Dialog", "Any"))

