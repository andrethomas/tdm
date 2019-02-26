import os

from PyQt5.QtCore import QSettings, QDir
from PyQt5.QtWidgets import QDialog, QLineEdit, QFormLayout, QPushButton, QGroupBox, QCheckBox, QLabel, QInputDialog, \
    QFileDialog, QMessageBox

from GUI import SpinBox, HLayout, VLayout, GroupBoxV


class BrokerDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(BrokerDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("MQTT Broker")
        self.settings = QSettings("{}/TDM/tdm.cfg".format(QDir.homePath()), QSettings.IniFormat)

        self.tls_path = self.settings.value("tls_path", "")

        gbHost = QGroupBox("Hostname and port")
        hfl = QFormLayout()
        self.hostname = QLineEdit()
        self.hostname.setText(self.settings.value("hostname", "localhost"))
        self.port = SpinBox(maximum=65535)
        self.port.setValue(self.settings.value("port", 1883, int))
        hfl.addRow("Hostname", self.hostname)
        hfl.addRow("Port", self.port)
        gbHost.setLayout(hfl)

        self.gbTLS = GroupBoxV("Use TLS")
        self.gbTLS.setCheckable(True)
        self.gbTLS.setChecked(self.settings.value("tls", False, bool))
        self.gbTLS.toggled.connect(self.toggle_tls)
        self.lbTLSPath = QLabel(os.path.split(self.tls_path)[1])
        pbTLSSelect = QPushButton("Select certificate")
        pbTLSSelect.clicked.connect(self.select_certificate)
        self.gbTLS.layout().addWidgets([self.lbTLSPath, pbTLSSelect])

        gbLogin = QGroupBox("Credentials [optional]")
        lfl = QFormLayout()
        self.username = QLineEdit()
        self.username.setText(self.settings.value("username", ""))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setText(self.settings.value("password", ""))
        lfl.addRow("Username", self.username)
        lfl.addRow("Password", self.password)
        gbLogin.setLayout(lfl)

        self.cbConnectStartup = QCheckBox("Connect on startup")
        self.cbConnectStartup.setChecked(self.settings.value("connect_on_startup", False, bool))

        hlBtn = HLayout()
        btnSave = QPushButton("Save")
        btnCancel = QPushButton("Cancel")
        hlBtn.addWidgets([btnSave, btnCancel])

        vl = VLayout()
        vl.addWidgets([gbHost, self.gbTLS, gbLogin, self.cbConnectStartup])
        vl.addLayout(hlBtn)

        self.setLayout(vl)

        btnSave.clicked.connect(self.check_settings)
        btnCancel.clicked.connect(self.reject)

    def toggle_tls(self, state):
        if state:
            self.port.setValue(8883)
        else:
            self.port.setValue(1883)

    def select_certificate(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open certificate file", os.path.split(self.tls_path)[0], "Certificates (*.crt);;All files (*.*)")
        if fname:
            self.tls_path = fname
            self.lbTLSPath.setText(os.path.split(fname)[1])

    def check_settings(self):
        if self.gbTLS.isChecked() and not self.tls_path:
            QMessageBox.warning(self, "Missing TLS path", "You've enabled TLS usage, but didn't specify the certificate file.")
        else:
            self.accept()

    def accept(self):
        self.settings.setValue("hostname", self.hostname.text())
        self.settings.setValue("port", self.port.value())
        self.settings.setValue("username", self.username.text())
        self.settings.setValue("password", self.password.text())
        self.settings.setValue("connect_on_startup", self.cbConnectStartup.isChecked())
        self.settings.setValue("tls", self.gbTLS.isChecked())
        self.settings.setValue("tls_path", self.tls_path)
        self.settings.sync()
        self.done(QDialog.Accepted)
