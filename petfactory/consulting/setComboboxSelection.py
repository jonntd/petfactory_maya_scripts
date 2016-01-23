#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
from PySide import QtGui

class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.setGeometry(60, 100, 250, 150)
        self.setWindowTitle('Icon')
        
        vbox = QtGui.QVBoxLayout(self)

        self.combobox = QtGui.QComboBox()
        
        itemDelegate = QtGui.QStyledItemDelegate()
        self.combobox.setItemDelegate(itemDelegate); 

        self.combobox.setStyleSheet('''QComboBox QAbstractItemView::item {
                    min-height: 30px;}
                    ''')
        vbox.addWidget(self.combobox)    

        self.show()

    def populateCombobox(self, itemNameList):
        self.combobox.addItems(itemNameList)

    def setIndex(self, index):
        self.combobox.setCurrentIndex(index)


        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    fruitList = ['Orange', 'Apple', 'Pear']
    ex.populateCombobox(fruitList)

    try:
        index = fruitList.index('Pear')
    except ValueError as e:
        print(e)
        return

    ex.setIndex(index)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()