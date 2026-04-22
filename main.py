import sys
import os
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import shutil

# Create folder for certificates
os.makedirs("certificates", exist_ok=True)

# Database setup
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS certificates(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    title TEXT,
    file_path TEXT
)
""")

conn.commit()


# ---------------- LOGIN WINDOW ----------------
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Certificate Vault - Login")
        self.setGeometry(300, 200, 300, 200)

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        signup_btn = QPushButton("Signup")

        login_btn.clicked.connect(self.login)
        signup_btn.clicked.connect(self.signup)

        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addWidget(signup_btn)

        self.setLayout(layout)

    def login(self):
        user = self.username.text()
        pwd = self.password.text()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = cursor.fetchone()

        if result:
            self.dashboard = Dashboard(user)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

    def signup(self):
        user = self.username.text()
        pwd = self.password.text()

        cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (user, pwd))
        conn.commit()
        QMessageBox.information(self, "Success", "User Registered!")


# ---------------- DASHBOARD ----------------
class Dashboard(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle(f"Welcome {user}")
        self.setGeometry(300, 200, 400, 400)

        layout = QVBoxLayout()

        self.list_widget = QListWidget()

        upload_btn = QPushButton("Upload Certificate")
        delete_btn = QPushButton("Delete Selected")

        upload_btn.clicked.connect(self.upload_file)
        delete_btn.clicked.connect(self.delete_file)

        layout.addWidget(self.list_widget)
        layout.addWidget(upload_btn)
        layout.addWidget(delete_btn)

        self.setLayout(layout)
        self.load_files()

    def load_files(self):
        self.list_widget.clear()
        cursor.execute("SELECT title FROM certificates WHERE user=?", (self.user,))
        for row in cursor.fetchall():
            self.list_widget.addItem(row[0])

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Certificate")

        if file_path:
            title, ok = QInputDialog.getText(self, "Title", "Enter Certificate Name:")
            if ok:
                dest = os.path.join("certificates", os.path.basename(file_path))
                shutil.copy(file_path, dest)

                cursor.execute("INSERT INTO certificates(user, title, file_path) VALUES (?, ?, ?)",
                               (self.user, title, dest))
                conn.commit()

                self.load_files()

    def delete_file(self):
        selected = self.list_widget.currentItem()
        if selected:
            title = selected.text()

            cursor.execute("DELETE FROM certificates WHERE user=? AND title=?", (self.user, title))
            conn.commit()

            self.load_files()


# ---------------- MAIN ----------------
app = QApplication(sys.argv)
window = LoginWindow()
window.show()
sys.exit(app.exec_())