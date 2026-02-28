import sys
import pymysql
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QDialog, QLineEdit, QHBoxLayout,
    QListWidget, QListWidgetItem, QHeaderView
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Настройки базы данных
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'go',
    'charset': 'utf8mb4'
}

# Глобальный список корзины
cart = []


def get_all_products():
    """Получить все товары из базы."""
    try:
        connection = pymysql.connect(**config)
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
        connection.close()
        return products
    except Exception as e:
        print(f"Ошибка доступа к базе: {e}")
        return []


def update_product_in_db(prod_id, name, description, price, category, manufacturer, article):
    """Обновить товар."""
    try:
        conn = pymysql.connect(**config)
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE products SET name=%s, description=%s, price=%s, category=%s, manufacturer=%s, article=%s WHERE id_product=%s
            """, (name, description, price, category, manufacturer, article, prod_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка обновления: {e}")


def add_product_to_db(name, description, price, category, manufacturer, article):
    """Добавить товар."""
    try:
        conn = pymysql.connect(**config)
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO products (name, description, price, category, manufacturer, article)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, description, price, category, manufacturer, article))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка добавления: {e}")


def delete_product_from_db(prod_id):
    """Удалить товар по id."""
    try:
        conn = pymysql.connect(**config)
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE id_product=%s", (prod_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка удаления: {e}")


class EditProductDialog(QDialog):
    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать товар")
        self.prod_id = product_data['id_product']
        layout = QVBoxLayout()

        self.name_edit = QLineEdit(product_data['name'])
        self.desc_edit = QLineEdit(product_data['description'])
        self.price_edit = QLineEdit(str(product_data['price']))
        self.category_edit = QLineEdit(product_data['category'])
        self.manuf_edit = QLineEdit(product_data['manufacturer'])
        self.article_edit = QLineEdit(product_data['article'])

        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Описание"))
        layout.addWidget(self.desc_edit)
        layout.addWidget(QLabel("Цена"))
        layout.addWidget(self.price_edit)
        layout.addWidget(QLabel("Категория"))
        layout.addWidget(self.category_edit)
        layout.addWidget(QLabel("Производитель"))
        layout.addWidget(self.manuf_edit)
        layout.addWidget(QLabel("Артикул"))
        layout.addWidget(self.article_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def save(self):
        try:
            update_product_in_db(
                self.prod_id,
                self.name_edit.text(),
                self.desc_edit.text(),
                float(self.price_edit.text()),
                self.category_edit.text(),
                self.manuf_edit.text(),
                self.article_edit.text()
            )
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {e}")


class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить товар")
        layout = QVBoxLayout()

        self.name_edit = QLineEdit()
        self.desc_edit = QLineEdit()
        self.price_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.manuf_edit = QLineEdit()
        self.article_edit = QLineEdit()

        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Описание"))
        layout.addWidget(self.desc_edit)
        layout.addWidget(QLabel("Цена"))
        layout.addWidget(self.price_edit)
        layout.addWidget(QLabel("Категория"))
        layout.addWidget(self.category_edit)
        layout.addWidget(QLabel("Производитель"))
        layout.addWidget(self.manuf_edit)
        layout.addWidget(QLabel("Артикул"))
        layout.addWidget(self.article_edit)

        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.add_product)
        layout.addWidget(btn_add)

        self.setLayout(layout)

    def add_product(self):
        try:
            add_product_to_db(
                self.name_edit.text(),
                self.desc_edit.text(),
                float(self.price_edit.text()),
                self.category_edit.text(),
                self.manuf_edit.text(),
                self.article_edit.text()
            )
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка добавления: {e}")


class CartDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Корзина")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.btn_delete = QPushButton("Удалить выбранный товар")
        self.btn_close = QPushButton("Закрыть")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.refresh_cart()
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_close.clicked.connect(self.close)

    def refresh_cart(self):
        self.list_widget.clear()
        for item in cart:
            self.list_widget.addItem(f"{item['name']} - {item['price']:.2f} руб.")

    def delete_selected(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите товар для удаления.")
            return
        for item in selected_items:
            idx = self.list_widget.row(item)
            del cart[idx]
        self.refresh_cart()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Магазин")
        self.setMinimumSize(900, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Кнопки для добавления товара и просмотра корзины
        btn_add_product = QPushButton("Добавить товар")
        btn_view_cart = QPushButton("Посмотреть корзину")
        btn_add_product.clicked.connect(self.open_add_product_dialog)
        btn_view_cart.clicked.connect(self.open_cart)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_add_product)
        btn_layout.addWidget(btn_view_cart)
        self.layout.addLayout(btn_layout)

        # Таблица товаров
        self.table_products = QTableWidget()
        self.layout.addWidget(self.table_products)

        self.central_widget.setLayout(self.layout)

        self.load_products()

    def load_products(self):
        products = get_all_products()
        self.table_products.clear()
        self.table_products.setColumnCount(11)
        self.table_products.setHorizontalHeaderLabels([
            "Фото", "Артикул", "Название", "Описание", "Цена",
            "Категория", "Производитель", "ID", "Редактировать", "Удалить", "Добавить в корзину"
        ])
        self.table_products.setRowCount(len(products))
        self.table_products.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for row, product in enumerate(products):
            # Фото - можно оставить как заглушку или вставить свое изображение
            label_photo = QLabel()
            pixmap = QPixmap("default.jpg")  # Предварительно подготовьте изображение или замените на реальный
            label_photo.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            self.table_products.setCellWidget(row, 0, label_photo)

            self.table_products.setItem(row, 1, QTableWidgetItem(str(product['article'])))
            self.table_products.setItem(row, 2, QTableWidgetItem(product['name']))
            self.table_products.setItem(row, 3, QTableWidgetItem(product['description']))
            self.table_products.setItem(row, 4, QTableWidgetItem(f"{product['price']:.2f}"))
            self.table_products.setItem(row, 5, QTableWidgetItem(product['category']))
            self.table_products.setItem(row, 6, QTableWidgetItem(product['manufacturer']))
            self.table_products.setItem(row, 7, QTableWidgetItem(str(product['id_product'])))

            # Редактировать
            btn_edit = QPushButton("Редактировать")
            btn_edit.clicked.connect(lambda _, p=product: self.edit_product(p))
            self.table_products.setCellWidget(row, 8, btn_edit)

            # Удалить
            btn_delete = QPushButton("Удалить")
            btn_delete.clicked.connect(lambda _, p_id=product['id_product']: self.delete_product(p_id))
            self.table_products.setCellWidget(row, 9, btn_delete)

            # В корзину
            btn_cart = QPushButton("В корзину")
            btn_cart.clicked.connect(lambda _, p=product: self.add_to_cart(p))
            self.table_products.setCellWidget(row, 10, btn_cart)

    def edit_product(self, product):
        dlg = EditProductDialog(product, self)
        if dlg.exec():
            self.load_products()

    def delete_product(self, prod_id):
        delete_product_from_db(prod_id)
        self.load_products()

    def add_to_cart(self, product):
        cart.append(product)
        QMessageBox.information(self, "Добавлено", f"Товар '{product['name']}' добавлен в корзину.")

    def open_add_product_dialog(self):
        dlg = AddProductDialog(self)
        if dlg.exec():
            self.load_products()

    def open_cart(self):
        dlg = CartDialog(self)
        dlg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())