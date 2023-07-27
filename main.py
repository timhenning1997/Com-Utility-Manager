import os, sys, inspect
from PyQt5.QtWidgets import QApplication
from ColorSchemeHandler import ColorSchemeHandler
from ConnectionHubWindow import ConnectionHubWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = ConnectionHubWindow()
    QApplication.setStyle("Fusion")

    colorSchemeHandler = ColorSchemeHandler(wnd)

    sys.exit(app.exec_())