import sys
import pymysql
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Настройки подключения к базе данных
config = {
    'host': 'localhost',     # Хост базы данных
    'user': 'root',  # Пользователь
    'password': 'root',    # Пароль
    'database': 'go',             # Название базы
    'charset': 'utf8mb4'
}

# Глобальный список корзины
cart = []

def get_all_product():
    """Получить все товары из базы данных."""
    try:
        connection = pymysql.connect(**config)
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
        connection.close()
        return products
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Торговый сервис")
        self.resize(1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Кнопка для просмотра корзины
        self.btn_show_cart = QPushButton("Посмотреть корзину")
        self.layout.addWidget(self.btn_show_cart)
        self.btn_show_cart.clicked.connect(self.show_cart)

        # Таблица для товаров
        self.table_products = QTableWidget()
        self.layout.addWidget(self.table_products)

        # Кнопка для загрузки товаров
        self.btn_load_products = QPushButton("Загрузить товары")
        self.layout.addWidget(self.btn_load_products)
        self.btn_load_products.clicked.connect(self.load_products)

        self.load_products()

    def load_products(self):
        products = get_all_product()

        self.table_products.clear()
        self.table_products.setColumnCount(10)
        self.table_products.setHorizontalHeaderLabels([
            "Фото", "Артикул", "Название", "Описание", "Цена",
            "Категория", "Производитель", "ID", "Добавить в корзину", "Удалить"
        ])
        self.table_products.setRowCount(len(products))
        for row_idx, product in enumerate(products):
            id_product = product.get('id_product', '')
            article = product.get('article', '')
            name = product.get('name', '')
            description = product.get('description', '')
            price = product.get('price', 0)
            category = product.get('category', '')
            manufacturer = product.get('manufacturer', '')

            # Фото
            label = QLabel()
            image_path = f"res/{article}.jpg"  # путь к изображению
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                label.setPixmap(pixmap)
            else:
                label.setText("Нет фото")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_products.setCellWidget(row_idx, 0, label)

            # Остальные данные
            self.table_products.setItem(row_idx, 1, QTableWidgetItem(str(article)))
            self.table_products.setItem(row_idx, 2, QTableWidgetItem(str(name)))
            self.table_products.setItem(row_idx, 3, QTableWidgetItem(str(description)))
            self.table_products.setItem(row_idx, 4, QTableWidgetItem(f"{price:.2f}"))
            self.table_products.setItem(row_idx, 5, QTableWidgetItem(str(category)))
            self.table_products.setItem(row_idx, 6, QTableWidgetItem(str(manufacturer)))
            self.table_products.setItem(row_idx, 7, QTableWidgetItem(str(id_product)))

            # Кнопка "Добавить в корзину"
            def make_add_to_cart(p=product):
                def add():
                    cart.append(p)
                    print(f"Добавлено: {p.get('name')}")
                return add

            btn_add = QPushButton("В корзину")
            btn_add.clicked.connect(make_add_to_cart())
            self.table_products.setCellWidget(row_idx, 8, btn_add)

            # Кнопка "Удалить" (просто удаляет строку из таблицы)
            def make_delete_row(row):
                def delete():
                    self.table_products.removeRow(row)
                return delete

            btn_del = QPushButton("Удалить")
            btn_del.clicked.connect(make_delete_row(row_idx))
            self.table_products.setCellWidget(row_idx, 9, btn_del)

    def show_cart(self):
        if not cart:
            QMessageBox.information(self, "Корзина", "Корзина пуста.")
            return
        total = sum(item.get('price', 0) for item in cart)
        details = "\n".join([f"{item.get('name', '')} - {item.get('price', 0):.2f}" for item in cart])
        QMessageBox.information(self, "Корзина", f"В корзине:\n{details}\n\nИтого: {total:.2f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())