# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_workflow_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(740, 681)
        Dialog.setMinimumSize(QtCore.QSize(400, 600))
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSpacing(1)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.TXT_DOMAINS = QtWidgets.QLineEdit(Dialog)
        self.TXT_DOMAINS.setReadOnly(True)
        self.TXT_DOMAINS.setObjectName("TXT_DOMAINS")
        self.horizontalLayout_6.addWidget(self.TXT_DOMAINS)
        self.BTN_DOMAINS = QtWidgets.QToolButton(Dialog)
        self.BTN_DOMAINS.setObjectName("BTN_DOMAINS")
        self.horizontalLayout_6.addWidget(self.BTN_DOMAINS)
        self.gridLayout.addLayout(self.horizontalLayout_6, 5, 2, 1, 1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setSpacing(1)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.TXT_ALIGNMENTS = QtWidgets.QLineEdit(Dialog)
        self.TXT_ALIGNMENTS.setReadOnly(True)
        self.TXT_ALIGNMENTS.setObjectName("TXT_ALIGNMENTS")
        self.horizontalLayout_7.addWidget(self.TXT_ALIGNMENTS)
        self.BTN_ALIGNMENTS = QtWidgets.QToolButton(Dialog)
        self.BTN_ALIGNMENTS.setObjectName("BTN_ALIGNMENTS")
        self.horizontalLayout_7.addWidget(self.BTN_ALIGNMENTS)
        self.gridLayout.addLayout(self.horizontalLayout_7, 6, 2, 1, 1)
        self.LBL_FILENAME_3 = QtWidgets.QLabel(Dialog)
        self.LBL_FILENAME_3.setObjectName("LBL_FILENAME_3")
        self.gridLayout.addWidget(self.LBL_FILENAME_3, 0, 0, 1, 3)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setSpacing(1)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.TXT_SPLITS = QtWidgets.QLineEdit(Dialog)
        self.TXT_SPLITS.setReadOnly(True)
        self.TXT_SPLITS.setObjectName("TXT_SPLITS")
        self.horizontalLayout_10.addWidget(self.TXT_SPLITS)
        self.BTN_SPLITS = QtWidgets.QToolButton(Dialog)
        self.BTN_SPLITS.setObjectName("BTN_SPLITS")
        self.horizontalLayout_10.addWidget(self.BTN_SPLITS)
        self.gridLayout.addLayout(self.horizontalLayout_10, 9, 2, 1, 1)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setSpacing(1)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.TXT_FUSIONS = QtWidgets.QLineEdit(Dialog)
        self.TXT_FUSIONS.setReadOnly(True)
        self.TXT_FUSIONS.setObjectName("TXT_FUSIONS")
        self.horizontalLayout_9.addWidget(self.TXT_FUSIONS)
        self.BTN_FUSIONS = QtWidgets.QToolButton(Dialog)
        self.BTN_FUSIONS.setObjectName("BTN_FUSIONS")
        self.horizontalLayout_9.addWidget(self.BTN_FUSIONS)
        self.gridLayout.addLayout(self.horizontalLayout_9, 8, 2, 1, 1)
        self.LBL_WARNI_ALIGNMENTS = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_ALIGNMENTS.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_ALIGNMENTS.setSizePolicy(sizePolicy)
        self.LBL_WARNI_ALIGNMENTS.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_ALIGNMENTS.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_ALIGNMENTS.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_ALIGNMENTS.setObjectName("LBL_WARNI_ALIGNMENTS")
        self.gridLayout.addWidget(self.LBL_WARNI_ALIGNMENTS, 6, 0, 1, 1)
        self.LBL_WARNI_SEQUENCES = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_SEQUENCES.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_SEQUENCES.setSizePolicy(sizePolicy)
        self.LBL_WARNI_SEQUENCES.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_SEQUENCES.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_SEQUENCES.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_SEQUENCES.setObjectName("LBL_WARNI_SEQUENCES")
        self.gridLayout.addWidget(self.LBL_WARNI_SEQUENCES, 2, 0, 1, 1)
        self.LBL_CHECKED = QtWidgets.QLabel(Dialog)
        self.LBL_CHECKED.setObjectName("LBL_CHECKED")
        self.gridLayout.addWidget(self.LBL_CHECKED, 15, 1, 1, 1)
        self.LBL_CLEANED = QtWidgets.QLabel(Dialog)
        self.LBL_CLEANED.setObjectName("LBL_CLEANED")
        self.gridLayout.addWidget(self.LBL_CLEANED, 14, 1, 1, 1)
        self.LBL_STITCHED = QtWidgets.QLabel(Dialog)
        self.LBL_STITCHED.setObjectName("LBL_STITCHED")
        self.gridLayout.addWidget(self.LBL_STITCHED, 13, 1, 1, 1)
        self.LBL_TREES = QtWidgets.QLabel(Dialog)
        self.LBL_TREES.setObjectName("LBL_TREES")
        self.gridLayout.addWidget(self.LBL_TREES, 7, 1, 1, 1)
        self.LBL_ALIGNMENTS = QtWidgets.QLabel(Dialog)
        self.LBL_ALIGNMENTS.setObjectName("LBL_ALIGNMENTS")
        self.gridLayout.addWidget(self.LBL_ALIGNMENTS, 6, 1, 1, 1)
        self.LBL_WARNI_SPLITS = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_SPLITS.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_SPLITS.setSizePolicy(sizePolicy)
        self.LBL_WARNI_SPLITS.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_SPLITS.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_SPLITS.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_SPLITS.setObjectName("LBL_WARNI_SPLITS")
        self.gridLayout.addWidget(self.LBL_WARNI_SPLITS, 9, 0, 1, 1)
        self.LBL_WARNI_SUBGRAPHS = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_SUBGRAPHS.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_SUBGRAPHS.setSizePolicy(sizePolicy)
        self.LBL_WARNI_SUBGRAPHS.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_SUBGRAPHS.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_SUBGRAPHS.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_SUBGRAPHS.setObjectName("LBL_WARNI_SUBGRAPHS")
        self.gridLayout.addWidget(self.LBL_WARNI_SUBGRAPHS, 12, 0, 1, 1)
        self.LBL_WARNI_SUBSETS = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_SUBSETS.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_SUBSETS.setSizePolicy(sizePolicy)
        self.LBL_WARNI_SUBSETS.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_SUBSETS.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_SUBSETS.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_SUBSETS.setObjectName("LBL_WARNI_SUBSETS")
        self.gridLayout.addWidget(self.LBL_WARNI_SUBSETS, 11, 0, 1, 1)
        self.LBL_WARNI_EDGES = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_EDGES.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_EDGES.setSizePolicy(sizePolicy)
        self.LBL_WARNI_EDGES.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_EDGES.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_EDGES.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_EDGES.setObjectName("LBL_WARNI_EDGES")
        self.gridLayout.addWidget(self.LBL_WARNI_EDGES, 3, 0, 1, 1)
        self.LBL_WARNI_STITCHED = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_STITCHED.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_STITCHED.setSizePolicy(sizePolicy)
        self.LBL_WARNI_STITCHED.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_STITCHED.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_STITCHED.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_STITCHED.setObjectName("LBL_WARNI_STITCHED")
        self.gridLayout.addWidget(self.LBL_WARNI_STITCHED, 13, 0, 1, 1)
        self.LBL_WARNI_CONSENSUS = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_CONSENSUS.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_CONSENSUS.setSizePolicy(sizePolicy)
        self.LBL_WARNI_CONSENSUS.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_CONSENSUS.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_CONSENSUS.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_CONSENSUS.setObjectName("LBL_WARNI_CONSENSUS")
        self.gridLayout.addWidget(self.LBL_WARNI_CONSENSUS, 10, 0, 1, 1)
        self.LBL_WARNI_FUSIONS = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_FUSIONS.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_FUSIONS.setSizePolicy(sizePolicy)
        self.LBL_WARNI_FUSIONS.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_FUSIONS.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_FUSIONS.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_FUSIONS.setObjectName("LBL_WARNI_FUSIONS")
        self.gridLayout.addWidget(self.LBL_WARNI_FUSIONS, 8, 0, 1, 1)
        self.LBL_WARNI_TREES = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_TREES.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_TREES.setSizePolicy(sizePolicy)
        self.LBL_WARNI_TREES.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_TREES.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_TREES.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_TREES.setObjectName("LBL_WARNI_TREES")
        self.gridLayout.addWidget(self.LBL_WARNI_TREES, 7, 0, 1, 1)
        self.LBL_WARNI_COMPONENTS = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_COMPONENTS.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_COMPONENTS.setSizePolicy(sizePolicy)
        self.LBL_WARNI_COMPONENTS.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_COMPONENTS.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_COMPONENTS.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_COMPONENTS.setObjectName("LBL_WARNI_COMPONENTS")
        self.gridLayout.addWidget(self.LBL_WARNI_COMPONENTS, 4, 0, 1, 1)
        self.LBL_WARNI_CHECKED = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_CHECKED.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_CHECKED.setSizePolicy(sizePolicy)
        self.LBL_WARNI_CHECKED.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_CHECKED.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_CHECKED.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_CHECKED.setObjectName("LBL_WARNI_CHECKED")
        self.gridLayout.addWidget(self.LBL_WARNI_CHECKED, 15, 0, 1, 1)
        self.LBL_WARNI_DOMAINS = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_DOMAINS.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_DOMAINS.setSizePolicy(sizePolicy)
        self.LBL_WARNI_DOMAINS.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_DOMAINS.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_DOMAINS.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_DOMAINS.setObjectName("LBL_WARNI_DOMAINS")
        self.gridLayout.addWidget(self.LBL_WARNI_DOMAINS, 5, 0, 1, 1)
        self.LBL_WARNI_FILENAME = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_FILENAME.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_FILENAME.setSizePolicy(sizePolicy)
        self.LBL_WARNI_FILENAME.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_FILENAME.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_FILENAME.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_FILENAME.setObjectName("LBL_WARNI_FILENAME")
        self.gridLayout.addWidget(self.LBL_WARNI_FILENAME, 1, 0, 1, 1)
        self.LBL_WARNI_CLEANED = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_WARNI_CLEANED.sizePolicy().hasHeightForWidth())
        self.LBL_WARNI_CLEANED.setSizePolicy(sizePolicy)
        self.LBL_WARNI_CLEANED.setMinimumSize(QtCore.QSize(4, 0))
        self.LBL_WARNI_CLEANED.setMaximumSize(QtCore.QSize(4, 16777215))
        self.LBL_WARNI_CLEANED.setStyleSheet("background:silver;\n"
"margin-top: 2px;\n"
"margin-bottom: 2px;")
        self.LBL_WARNI_CLEANED.setObjectName("LBL_WARNI_CLEANED")
        self.gridLayout.addWidget(self.LBL_WARNI_CLEANED, 14, 0, 1, 1)
        self.LBL_SUBSETS = QtWidgets.QLabel(Dialog)
        self.LBL_SUBSETS.setObjectName("LBL_SUBSETS")
        self.gridLayout.addWidget(self.LBL_SUBSETS, 11, 1, 1, 1)
        self.FRA_PAUSED = QtWidgets.QFrame(Dialog)
        self.FRA_PAUSED.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FRA_PAUSED.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FRA_PAUSED.setObjectName("FRA_PAUSED")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.FRA_PAUSED)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LBL_PAUSED = QtWidgets.QLabel(self.FRA_PAUSED)
        self.LBL_PAUSED.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_PAUSED.setObjectName("LBL_PAUSED")
        self.verticalLayout.addWidget(self.LBL_PAUSED)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.BTN_CONTINUE = QtWidgets.QPushButton(self.FRA_PAUSED)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_CONTINUE.sizePolicy().hasHeightForWidth())
        self.BTN_CONTINUE.setSizePolicy(sizePolicy)
        self.BTN_CONTINUE.setObjectName("BTN_CONTINUE")
        self.horizontalLayout_2.addWidget(self.BTN_CONTINUE)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.LBL_NEXT = QtWidgets.QLabel(self.FRA_PAUSED)
        self.LBL_NEXT.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_NEXT.setObjectName("LBL_NEXT")
        self.verticalLayout.addWidget(self.LBL_NEXT)
        self.line = QtWidgets.QFrame(self.FRA_PAUSED)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.LBL_CLOSE = QtWidgets.QLabel(self.FRA_PAUSED)
        self.LBL_CLOSE.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_CLOSE.setObjectName("LBL_CLOSE")
        self.verticalLayout.addWidget(self.LBL_CLOSE)
        self.gridLayout.addWidget(self.FRA_PAUSED, 16, 0, 1, 5)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setSpacing(1)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.TXT_STITCHED = QtWidgets.QLineEdit(Dialog)
        self.TXT_STITCHED.setReadOnly(True)
        self.TXT_STITCHED.setObjectName("TXT_STITCHED")
        self.horizontalLayout_14.addWidget(self.TXT_STITCHED)
        self.BTN_STITCHED = QtWidgets.QToolButton(Dialog)
        self.BTN_STITCHED.setObjectName("BTN_STITCHED")
        self.horizontalLayout_14.addWidget(self.BTN_STITCHED)
        self.gridLayout.addLayout(self.horizontalLayout_14, 13, 2, 1, 1)
        self.LBL_FUSIONS = QtWidgets.QLabel(Dialog)
        self.LBL_FUSIONS.setObjectName("LBL_FUSIONS")
        self.gridLayout.addWidget(self.LBL_FUSIONS, 8, 1, 1, 1)
        self.LBL_COMPONENTS = QtWidgets.QLabel(Dialog)
        self.LBL_COMPONENTS.setObjectName("LBL_COMPONENTS")
        self.gridLayout.addWidget(self.LBL_COMPONENTS, 4, 1, 1, 1)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setSpacing(1)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.TXT_CONSENSUS = QtWidgets.QLineEdit(Dialog)
        self.TXT_CONSENSUS.setReadOnly(True)
        self.TXT_CONSENSUS.setObjectName("TXT_CONSENSUS")
        self.horizontalLayout_11.addWidget(self.TXT_CONSENSUS)
        self.BTN_CONSENSUS = QtWidgets.QToolButton(Dialog)
        self.BTN_CONSENSUS.setObjectName("BTN_CONSENSUS")
        self.horizontalLayout_11.addWidget(self.BTN_CONSENSUS)
        self.gridLayout.addLayout(self.horizontalLayout_11, 10, 2, 1, 1)
        self.LBL_SEQUENCES = QtWidgets.QLabel(Dialog)
        self.LBL_SEQUENCES.setObjectName("LBL_SEQUENCES")
        self.gridLayout.addWidget(self.LBL_SEQUENCES, 2, 1, 1, 1)
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setSpacing(1)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.TXT_CHECKED = QtWidgets.QLineEdit(Dialog)
        self.TXT_CHECKED.setReadOnly(True)
        self.TXT_CHECKED.setObjectName("TXT_CHECKED")
        self.horizontalLayout_17.addWidget(self.TXT_CHECKED)
        self.BTN_CHECKED = QtWidgets.QToolButton(Dialog)
        self.BTN_CHECKED.setObjectName("BTN_CHECKED")
        self.horizontalLayout_17.addWidget(self.BTN_CHECKED)
        self.gridLayout.addLayout(self.horizontalLayout_17, 15, 2, 1, 1)
        self.LBL_FILENAME = QtWidgets.QLabel(Dialog)
        self.LBL_FILENAME.setObjectName("LBL_FILENAME")
        self.gridLayout.addWidget(self.LBL_FILENAME, 1, 1, 1, 1)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setSpacing(1)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.TXT_SUBSETS = QtWidgets.QLineEdit(Dialog)
        self.TXT_SUBSETS.setReadOnly(True)
        self.TXT_SUBSETS.setObjectName("TXT_SUBSETS")
        self.horizontalLayout_12.addWidget(self.TXT_SUBSETS)
        self.BTN_SUBSETS = QtWidgets.QToolButton(Dialog)
        self.BTN_SUBSETS.setObjectName("BTN_SUBSETS")
        self.horizontalLayout_12.addWidget(self.BTN_SUBSETS)
        self.gridLayout.addLayout(self.horizontalLayout_12, 11, 2, 1, 1)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setSpacing(1)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.TXT_SUBGRAPHS = QtWidgets.QLineEdit(Dialog)
        self.TXT_SUBGRAPHS.setReadOnly(True)
        self.TXT_SUBGRAPHS.setObjectName("TXT_SUBGRAPHS")
        self.horizontalLayout_13.addWidget(self.TXT_SUBGRAPHS)
        self.BTN_SUBGRAPHS = QtWidgets.QToolButton(Dialog)
        self.BTN_SUBGRAPHS.setObjectName("BTN_SUBGRAPHS")
        self.horizontalLayout_13.addWidget(self.BTN_SUBGRAPHS)
        self.gridLayout.addLayout(self.horizontalLayout_13, 12, 2, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.TXT_EDGES = QtWidgets.QLineEdit(Dialog)
        self.TXT_EDGES.setReadOnly(True)
        self.TXT_EDGES.setObjectName("TXT_EDGES")
        self.horizontalLayout_4.addWidget(self.TXT_EDGES)
        self.BTN_EDGES = QtWidgets.QToolButton(Dialog)
        self.BTN_EDGES.setObjectName("BTN_EDGES")
        self.horizontalLayout_4.addWidget(self.BTN_EDGES)
        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 2, 1, 1)
        self.LBL_SUBGRAPHS = QtWidgets.QLabel(Dialog)
        self.LBL_SUBGRAPHS.setObjectName("LBL_SUBGRAPHS")
        self.gridLayout.addWidget(self.LBL_SUBGRAPHS, 12, 1, 1, 1)
        self.LBL_SPLITS = QtWidgets.QLabel(Dialog)
        self.LBL_SPLITS.setObjectName("LBL_SPLITS")
        self.gridLayout.addWidget(self.LBL_SPLITS, 9, 1, 1, 1)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setSpacing(1)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.TXT_TREES = QtWidgets.QLineEdit(Dialog)
        self.TXT_TREES.setReadOnly(True)
        self.TXT_TREES.setObjectName("TXT_TREES")
        self.horizontalLayout_8.addWidget(self.TXT_TREES)
        self.BTN_TREES = QtWidgets.QToolButton(Dialog)
        self.BTN_TREES.setObjectName("BTN_TREES")
        self.horizontalLayout_8.addWidget(self.BTN_TREES)
        self.gridLayout.addLayout(self.horizontalLayout_8, 7, 2, 1, 1)
        self.LBL_CONSENSUS = QtWidgets.QLabel(Dialog)
        self.LBL_CONSENSUS.setObjectName("LBL_CONSENSUS")
        self.gridLayout.addWidget(self.LBL_CONSENSUS, 10, 1, 1, 1)
        self.LBL_DOMAINS = QtWidgets.QLabel(Dialog)
        self.LBL_DOMAINS.setObjectName("LBL_DOMAINS")
        self.gridLayout.addWidget(self.LBL_DOMAINS, 5, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 17, 1, 1, 3)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setSpacing(1)
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.TXT_CLEANED = QtWidgets.QLineEdit(Dialog)
        self.TXT_CLEANED.setReadOnly(True)
        self.TXT_CLEANED.setObjectName("TXT_CLEANED")
        self.horizontalLayout_15.addWidget(self.TXT_CLEANED)
        self.BTN_CLEANED = QtWidgets.QToolButton(Dialog)
        self.BTN_CLEANED.setObjectName("BTN_CLEANED")
        self.horizontalLayout_15.addWidget(self.BTN_CLEANED)
        self.gridLayout.addLayout(self.horizontalLayout_15, 14, 2, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.TXT_SEQUENCES = QtWidgets.QLineEdit(Dialog)
        self.TXT_SEQUENCES.setReadOnly(True)
        self.TXT_SEQUENCES.setObjectName("TXT_SEQUENCES")
        self.horizontalLayout_3.addWidget(self.TXT_SEQUENCES)
        self.BTN_SEQUENCES = QtWidgets.QToolButton(Dialog)
        self.BTN_SEQUENCES.setObjectName("BTN_SEQUENCES")
        self.horizontalLayout_3.addWidget(self.BTN_SEQUENCES)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 2, 1, 1)
        self.LBL_EDGES = QtWidgets.QLabel(Dialog)
        self.LBL_EDGES.setObjectName("LBL_EDGES")
        self.gridLayout.addWidget(self.LBL_EDGES, 3, 1, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(1)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.TXT_COMPONENTS = QtWidgets.QLineEdit(Dialog)
        self.TXT_COMPONENTS.setReadOnly(True)
        self.TXT_COMPONENTS.setObjectName("TXT_COMPONENTS")
        self.horizontalLayout_5.addWidget(self.TXT_COMPONENTS)
        self.BTN_COMPONENTS = QtWidgets.QToolButton(Dialog)
        self.BTN_COMPONENTS.setObjectName("BTN_COMPONENTS")
        self.horizontalLayout_5.addWidget(self.BTN_COMPONENTS)
        self.gridLayout.addLayout(self.horizontalLayout_5, 4, 2, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.TXT_FILENAME = QtWidgets.QLineEdit(Dialog)
        self.TXT_FILENAME.setReadOnly(True)
        self.TXT_FILENAME.setObjectName("TXT_FILENAME")
        self.horizontalLayout.addWidget(self.TXT_FILENAME)
        self.BTN_FILENAME = QtWidgets.QToolButton(Dialog)
        self.BTN_FILENAME.setObjectName("BTN_FILENAME")
        self.horizontalLayout.addWidget(self.BTN_FILENAME)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.BTN_DOMAINS.setText(_translate("Dialog", "▼"))
        self.BTN_ALIGNMENTS.setText(_translate("Dialog", "▼"))
        self.LBL_FILENAME_3.setText(_translate("Dialog", "Workflow"))
        self.LBL_FILENAME_3.setProperty("style", _translate("Dialog", "title"))
        self.BTN_SPLITS.setText(_translate("Dialog", "▼"))
        self.BTN_FUSIONS.setText(_translate("Dialog", "▼"))
        self.LBL_CHECKED.setText(_translate("Dialog", "Checked"))
        self.LBL_CLEANED.setText(_translate("Dialog", "Cleaned"))
        self.LBL_STITCHED.setText(_translate("Dialog", "Stitched"))
        self.LBL_TREES.setText(_translate("Dialog", "Trees"))
        self.LBL_ALIGNMENTS.setText(_translate("Dialog", "Alignments"))
        self.LBL_SUBSETS.setText(_translate("Dialog", "Subsets"))
        self.LBL_PAUSED.setText(_translate("Dialog", "The wizard has paused for you to review the progress."))
        self.BTN_CONTINUE.setText(_translate("Dialog", "CLICK TO CONTINUE"))
        self.BTN_CONTINUE.setProperty("style", _translate("Dialog", "completed"))
        self.LBL_NEXT.setText(_translate("Dialog", "Next step: <a href=\"action:wizard_next\">{}</a>."))
        self.LBL_CLOSE.setText(_translate("Dialog", "You can always <a href=\"action:stop_wizard\">stop</a> using the wizard and continue manually."))
        self.BTN_STITCHED.setText(_translate("Dialog", "▼"))
        self.LBL_FUSIONS.setText(_translate("Dialog", "Fusions"))
        self.LBL_COMPONENTS.setText(_translate("Dialog", "Components"))
        self.BTN_CONSENSUS.setText(_translate("Dialog", "▼"))
        self.LBL_SEQUENCES.setText(_translate("Dialog", "Sequences"))
        self.BTN_CHECKED.setText(_translate("Dialog", "▼"))
        self.LBL_FILENAME.setText(_translate("Dialog", "File name"))
        self.BTN_SUBSETS.setText(_translate("Dialog", "▼"))
        self.BTN_SUBGRAPHS.setText(_translate("Dialog", "▼"))
        self.BTN_EDGES.setText(_translate("Dialog", "▼"))
        self.LBL_SUBGRAPHS.setText(_translate("Dialog", "Subgraphs"))
        self.LBL_SPLITS.setText(_translate("Dialog", "Splits"))
        self.BTN_TREES.setText(_translate("Dialog", "▼"))
        self.LBL_CONSENSUS.setText(_translate("Dialog", "Consensus"))
        self.LBL_DOMAINS.setText(_translate("Dialog", "Domains"))
        self.BTN_CLEANED.setText(_translate("Dialog", "▼"))
        self.BTN_SEQUENCES.setText(_translate("Dialog", "▼"))
        self.LBL_EDGES.setText(_translate("Dialog", "Edges"))
        self.BTN_COMPONENTS.setText(_translate("Dialog", "▼"))
        self.BTN_FILENAME.setText(_translate("Dialog", "▼"))


