from PySide import QtCore, QtGui
from functools import partial

'''
import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)

'''
def add_spinbox(label, parent_layout, min=None, max=None, default=None, double_spinbox=False):
    
    horiz_layout = QtGui.QHBoxLayout()
    parent_layout.addLayout(horiz_layout)

    label = QtGui.QLabel(label)
    label.setMinimumWidth(100)
    horiz_layout.addWidget(label)

    horiz_layout.addStretch()

    spinbox = QtGui.QSpinBox() if not double_spinbox else QtGui.QDoubleSpinBox()

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