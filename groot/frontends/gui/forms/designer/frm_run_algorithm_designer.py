# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_run_algorithm_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(853, 673)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LBL_TITLE = QtWidgets.QLabel(Dialog)
        self.LBL_TITLE.setProperty("style", "title")
        self.LBL_TITLE.setObjectName("LBL_TITLE")
        self.verticalLayout.addWidget(self.LBL_TITLE)
        self.LBL_WARN_REQUIREMENTS = QtWidgets.QLabel(Dialog)
        self.LBL_WARN_REQUIREMENTS.setProperty("style", "warning")
        self.LBL_WARN_REQUIREMENTS.setObjectName("LBL_WARN_REQUIREMENTS")
        self.verticalLayout.addWidget(self.LBL_WARN_REQUIREMENTS)
        self.LBL_WARN_ALREADY = QtWidgets.QLabel(Dialog)
        self.LBL_WARN_ALREADY.setProperty("style", "warning")
        self.LBL_WARN_ALREADY.setObjectName("LBL_WARN_ALREADY")
        self.verticalLayout.addWidget(self.LBL_WARN_ALREADY)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setProperty("style", "heading")
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.FRA_MAIN = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FRA_MAIN.sizePolicy().hasHeightForWidth())
        self.FRA_MAIN.setSizePolicy(sizePolicy)
        self.FRA_MAIN.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FRA_MAIN.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FRA_MAIN.setObjectName("FRA_MAIN")
        self.verticalLayout.addWidget(self.FRA_MAIN)
        self.LBL_HELP = QtWidgets.QLabel(Dialog)
        self.LBL_HELP.setProperty("style", "helpbox")
        self.LBL_HELP.setObjectName("LBL_HELP")
        self.verticalLayout.addWidget(self.LBL_HELP)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.BTN_OK = QtWidgets.QPushButton(Dialog)
        self.BTN_OK.setObjectName("BTN_OK")
        self.horizontalLayout.addWidget(self.BTN_OK)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.LBL_TITLE.setText(_translate("Dialog", "Generate tree"))
        self.LBL_WARN_REQUIREMENTS.setText(_translate("Dialog", "text goes here"))
        self.LBL_WARN_ALREADY.setText(_translate("Dialog", "text goes here"))
        self.label_2.setText(_translate("Dialog", "Algorithm"))
        self.LBL_HELP.setText(_translate("Dialog", "Select the algorithm you\'d like to use. Remember, you can add your own algorithms to Groot as well!"))
        self.BTN_OK.setText(_translate("Dialog", "OK"))

