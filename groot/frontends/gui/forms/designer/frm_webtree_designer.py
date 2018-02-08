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
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_21.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_21.setSpacing(8)
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.BTN_SELECTION = QtWidgets.QPushButton(self.frame)
        self.BTN_SELECTION.setAutoDefault(False)
        self.BTN_SELECTION.setObjectName("BTN_SELECTION")
        self.horizontalLayout_21.addWidget(self.BTN_SELECTION)
        self.line = QtWidgets.QFrame(self.frame)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_21.addWidget(self.line)
        self.BTN_SAVE_TO_FILE = QtWidgets.QPushButton(self.frame)
        self.BTN_SAVE_TO_FILE.setAutoDefault(False)
        self.BTN_SAVE_TO_FILE.setObjectName("BTN_SAVE_TO_FILE")
        self.horizontalLayout_21.addWidget(self.BTN_SAVE_TO_FILE)
        self.BTN_BROWSE_HERE = QtWidgets.QPushButton(self.frame)
        self.BTN_BROWSE_HERE.setAutoDefault(False)
        self.BTN_BROWSE_HERE.setObjectName("BTN_BROWSE_HERE")
        self.horizontalLayout_21.addWidget(self.BTN_BROWSE_HERE)
        self.BTN_SYSTEM_BROWSER = QtWidgets.QPushButton(self.frame)
        self.BTN_SYSTEM_BROWSER.setAutoDefault(False)
        self.BTN_SYSTEM_BROWSER.setObjectName("BTN_SYSTEM_BROWSER")
        self.horizontalLayout_21.addWidget(self.BTN_SYSTEM_BROWSER)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_21.addItem(spacerItem)
        self.verticalLayout.addWidget(self.frame)
        self.LBL_NO_TREES_WARNING = QtWidgets.QLabel(Dialog)
        self.LBL_NO_TREES_WARNING.setObjectName("LBL_NO_TREES_WARNING")
        self.verticalLayout.addWidget(self.LBL_NO_TREES_WARNING)
        self.LBL_NO_VISJS_WARNING = QtWidgets.QLabel(Dialog)
        self.LBL_NO_VISJS_WARNING.setObjectName("LBL_NO_VISJS_WARNING")
        self.verticalLayout.addWidget(self.LBL_NO_VISJS_WARNING)
        self.LBL_SELECTION_WARNING = QtWidgets.QLabel(Dialog)
        self.LBL_SELECTION_WARNING.setObjectName("LBL_SELECTION_WARNING")
        self.verticalLayout.addWidget(self.LBL_SELECTION_WARNING)
        self.LBL_TITLE = QtWidgets.QLabel(Dialog)
        self.LBL_TITLE.setObjectName("LBL_TITLE")
        self.verticalLayout.addWidget(self.LBL_TITLE)
        self.WIDGET_OTHER = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.WIDGET_OTHER.sizePolicy().hasHeightForWidth())
        self.WIDGET_OTHER.setSizePolicy(sizePolicy)
        self.WIDGET_OTHER.setObjectName("WIDGET_OTHER")
        self.gridLayout = QtWidgets.QGridLayout(self.WIDGET_OTHER)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.LBL_NO_INBUILT = QtWidgets.QLabel(self.WIDGET_OTHER)
        self.LBL_NO_INBUILT.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_NO_INBUILT.setObjectName("LBL_NO_INBUILT")
        self.gridLayout.addWidget(self.LBL_NO_INBUILT, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.WIDGET_OTHER)
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
        self.BTN_SAVE_TO_FILE.setText(_translate("Dialog", "Save to file"))
        self.BTN_BROWSE_HERE.setText(_translate("Dialog", "Inbuilt browser"))
        self.BTN_SYSTEM_BROWSER.setText(_translate("Dialog", "System browser"))
        self.LBL_NO_TREES_WARNING.setText(_translate("Dialog", "You have no trees or graphs, go to the <a href=\"action:show_workflow\">workflow</a>."))
        self.LBL_NO_TREES_WARNING.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_NO_VISJS_WARNING.setText(_translate("Dialog", "vis.js is not <a href=\"action:show_options\">configured</a>. You won\'t be able to see the graphs."))
        self.LBL_NO_VISJS_WARNING.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_SELECTION_WARNING.setText(_translate("Dialog", "There are no trees in the <a href=\"action:show_selection\">current selection</a>."))
        self.LBL_SELECTION_WARNING.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_TITLE.setText(_translate("Dialog", "TextLabel"))
        self.LBL_TITLE.setProperty("style", _translate("Dialog", "title"))
        self.LBL_NO_INBUILT.setText(_translate("Dialog", "<p>The inbuilt browser has been turned off in the <a href=\"action:show_options\">settings</a>.</p>\n"
"<p>Either <a href=\"action:enable_inbuilt_browser\">enable</a> the inbuilt browser or use the external browser.</p>"))
