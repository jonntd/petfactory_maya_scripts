from PySide import QtCore, QtGui
from functools import partial

import pymel.core as pm

import petfactory.util.verify as pet_verify
reload(pet_verify)

'''
import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

'''
def add_spinbox(label, parent_layout, min=None, max=None, default=None, double_spinbox=False, decimals=2, singlestep=None, label_width=100):
    
    horiz_layout = QtGui.QHBoxLayout()
    parent_layout.addLayout(horiz_layout)

    label = QtGui.QLabel(label)
    label.setMinimumWidth(label_width)
    horiz_layout.addWidget(label)

    horiz_layout.addStretch()

    if double_spinbox:
        spinbox = QtGui.QDoubleSpinBox()
        spinbox.setDecimals(decimals)
        if singlestep is not None:
            spinbox.setSingleStep(singlestep)

    else:
        spinbox = QtGui.QSpinBox()
        if singlestep is not None:
            spinbox.setSingleStep(singlestep)

    if min:
        spinbox.setMinimum(min)
    if max:
        spinbox.setMaximum(max)
    if default:
        spinbox.setValue(default)

    

    horiz_layout.addWidget(spinbox)
    spinbox.setMinimumWidth(100)

    return spinbox


def add_populate_lineedit(label, parent_layout, callback=None, kwargs={}):
    
    horiz_layout = QtGui.QHBoxLayout()
    parent_layout.addLayout(horiz_layout)

    button = QtGui.QPushButton(label)
    button.setMinimumWidth(80)
    horiz_layout.addWidget(button)

    lineedit = QtGui.QLineEdit()
    horiz_layout.addWidget(lineedit)
    lineedit.setMinimumWidth(100)

    
    if callback is not None:
        
        kwargs['lineedit'] = lineedit
        button.clicked.connect(partial(callback, **kwargs))

    return lineedit

def add_selection_to_lineedit(lineedit, nodetype):

    is_valid = pet_verify.verify_selection(node_type=nodetype)

    if is_valid:
        node_name = pet_verify.to_transform(pm.ls(sl=True)[0]).shortName()
        lineedit.setText(node_name)

def add_filtered_populate_lineedit(label, parent_layout, nodetype):
    
    horiz_layout = QtGui.QHBoxLayout()
    parent_layout.addLayout(horiz_layout)

    button = QtGui.QPushButton(label)
    button.setMinimumWidth(80)
    horiz_layout.addWidget(button)

    lineedit = QtGui.QLineEdit()
    horiz_layout.addWidget(lineedit)
    lineedit.setMinimumWidth(100)

    button.clicked.connect(partial(add_selection_to_lineedit, lineedit, nodetype))

    return lineedit

def labeled_lineedit(label, parent_layout):
    
    horiz_layout = QtGui.QHBoxLayout()
    parent_layout.addLayout(horiz_layout)

    label = QtGui.QLabel(label)
    label.setMinimumWidth(80)
    horiz_layout.addWidget(label)
    label.setAlignment(QtCore.Qt.AlignRight)

    lineedit = QtGui.QLineEdit()
    horiz_layout.addWidget(lineedit)
    lineedit.setMinimumWidth(100)

    return lineedit

def labeled_checkbox(label, parent_layout):
    
    horiz_layout = QtGui.QHBoxLayout()
    parent_layout.addLayout(horiz_layout)

    label = QtGui.QLabel(label)
    label.setMinimumWidth(80)
    horiz_layout.addWidget(label)
    label.setAlignment(QtCore.Qt.AlignRight)

    checkbox = QtGui.QCheckBox()
    horiz_layout.addWidget(checkbox)
    checkbox.setMinimumWidth(100)

    horiz_layout.addStretch()

    return checkbox

def labeled_combobox(label, parent_layout, items=[]):
    
    horiz_layout = QtGui.QHBoxLayout()
    parent_layout.addLayout(horiz_layout)

    label = QtGui.QLabel(label)
    label.setMinimumWidth(80)
    horiz_layout.addWidget(label)
    label.setAlignment(QtCore.Qt.AlignRight)

    combobox = QtGui.QComboBox()
    horiz_layout.addWidget(combobox)
    combobox.setMinimumWidth(100)
    combobox.addItems(items)

    horiz_layout.addStretch()

    return combobox