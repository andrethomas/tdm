import os

from PyQt5 import QtCore
from PyQt5.QtCore import QDir
from http.server import HTTPServer, SimpleHTTPRequestHandler


class OTAHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'html')
        self.end_headers()


class ServerThread(QtCore.QThread):
    def configure(self, ip, port, working_dir):
        self.ip = ip
        self.port = port
        os.chdir(working_dir)

    def run(self):
        self._server = HTTPServer((self.ip, self.port), OTAHandler)
        self._server.serve_forever()

    def stop(self):
        self._server.shutdown()
        self._server.socket.close()
        self.wait()

class OTAServer(QtCore.QObject):
    Waiting = 0
    Listening = 1

    listening = QtCore.pyqtSignal()
    waiting = QtCore.pyqtSignal()

    request = QtCore.pyqtSignal()

    stateChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(OTAServer, self).__init__(parent)

        self._ip = "0.0.0.0"
        self._port = 5000
        self._working_directory = QDir.homePath() + "/Projects"

        self._state = OTAServer.Waiting

        self._thread = None

    @QtCore.pyqtProperty(int, notify=stateChanged)
    def state(self):
        return self._state

    @QtCore.pyqtProperty(str)
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, ip):
        self._ip = ip

    @QtCore.pyqtProperty(int)
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = port

    @QtCore.pyqtSlot()
    def startListening(self):
        self._thread = ServerThread()
        self._thread.configure(self._ip, self._port, self._working_directory)
        self._thread.start()

    @QtCore.pyqtSlot()
    def stopListening(self):
        self.m_client.loop_stop()
        self.m_client.disconnect()



    # # callbacks
    # def on_message(self, mqttc, obj, msg):
    #     topic = msg.topic
    #     mstr = msg.payload.decode("ascii")
    #     # print("on_message", mstr, obj, mqttc)
    #     self.messageSignal.emit(topic, mstr)
    #
    # def on_connect(self, *args):
    #     # print("on_connect", client, userdata, rc)
    #     rc = args[3]
    #     if rc == 0:
    #         self.state = MqttClient.Connected
    #         self.connected.emit()
    #     else:
    #         self.state = MqttClient.Disconnected
    #         self.connectError.emit(rc)
    #
    # def on_disconnect(self, *args):
    #     # print("on_disconnect", args)
    #     self.state = MqttClient.Disconnected
    #     self.disconnected.emit()

