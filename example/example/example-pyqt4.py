# -*- coding: utf8 -*-

from PyQt4.QtGui import QApplication, QDialog, QIcon
from PyQt4.QtCore import QLocale, QTranslator

from ui.ui_dialog import Ui_Dialog

import example_rc # __IGNORE_WARNING__


class Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        super(Dialog, self).__init__(parent)
        self.setupUi(self)
        self.testButton.clicked.connect(self.toggleIcon)

    def toggleIcon(self):
        self.testIcon.setVisible(not self.testIcon.isVisible())

    def accept(self):
        print('accept')
        super(Dialog, self).accept()

    def reject(self):
        print('reject')
        super(Dialog, self).reject()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/images/icon.png"))
    locale = QLocale()
    if locale.name() != "C":
        translator = QTranslator()
        if translator.load(locale, ':/i18n/example', '_', 'i18n'):
            if app.installTranslator(translator):
                print('translation %s installed' % locale.name())
    dialog = Dialog()
    dialog.show()
    sys.exit(app.exec_())
