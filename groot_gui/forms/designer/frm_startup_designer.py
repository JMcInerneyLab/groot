# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot_gui/forms/designer/frm_startup_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(652, 706)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setStyleSheet("QFrame[style=\"grootunique\"]\n"
"{\n"
"background: qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(208, 208, 208, 255), stop:0.0985222 rgba(255, 255, 255, 255), stop:1 rgba(229, 229, 229, 255));\n"
"color: black;\n"
"}")
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.LBL_FIRST_MESSAGE = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_FIRST_MESSAGE.sizePolicy().hasHeightForWidth())
        self.LBL_FIRST_MESSAGE.setSizePolicy(sizePolicy)
        self.LBL_FIRST_MESSAGE.setStyleSheet("QLabel\n"
"{\n"
"padding: 32;\n"
"background: transparent;\n"
"}")
        self.LBL_FIRST_MESSAGE.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LBL_FIRST_MESSAGE.setObjectName("LBL_FIRST_MESSAGE")
        self.gridLayout_2.addWidget(self.LBL_FIRST_MESSAGE, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.frame.setProperty("style", _translate("Dialog", "grootunique"))
        self.LBL_FIRST_MESSAGE.setText(_translate("Dialog", "<html><head/><body>\n"
"<h1>Groot</h1><img src=\":/groot/groot_logo.png\" width=128 height=85 align=\"right\" />\n"
"<p><i>Groot version $(VERSION)</i></p>\n"
"<p>Would you like to:</p>\n"
"<ul>\n"
"<li>Grootle around yourself in the <a href=\"action:view_workflow\">workflow</a>.</li>\n"
"<li>Have a magical <a href=\"action:view_wizard\">wizard</a> do everything for you</li>\n"
"<li>Stand alone and <a href=\"action:dismiss_startup_screen\">dismiss</a> this message.</li>\n"
"<li>View the <a href=\"action:view_help\">documentation</a> online.</li>\n"
"</ul>\n"
"$(RECENT_FILES)\n"
"</body></html>"))


