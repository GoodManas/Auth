from PyQt6 import QtWidgets
import sys
from auth_window import Ui_MainWindow
from window_admin import Ui_Form
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from connect import check


class Admin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.auth)

    def auth(self):
        try:
            Login = self.ui.lineEdit_login.text()
            Password = self.ui.lineEdit_password.text()
            print(Login,Password)

            user_data = check(Login,Password)
            id_user, role, login, password = user_data

            if role == 1:
                QtWidgets.QMessageBox.information(
                    self, "успех",
                    f"добро пожаловать администратор, {login}"
                )
                self.open_window_admin()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self,"Error",f"Error {e}")

    def open_window_admin(self):
        self.window_admin = Admin()
        self.window_admin.show()
        self.close()








if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())