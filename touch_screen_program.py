import sys
import PyQt5
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
from pynput.mouse import Controller
import screen_brightness_control as sbc
import ctypes
from ctypes import wintypes as w
import win32api
import win32gui
import subprocess
import webbrowser
import psutil

class Worker(QThread):
    timeout = pyqtSignal(list)

    def __init__(self, btn_data, sys_data):
        super().__init__()
        self.mouse = Controller()
        self.state = ['0.0%' for i in range(len(sys_data))] + ['0,0']
        self.btn_data = btn_data
        self.sys_data = sys_data
    def run(self):
        while True:
            self.timeout.emit(self.state)
            self.state = []
            for i in range(len(self.sys_data)):
                labels_information = self.btn_data[self.sys_data[i]][-1][1].split("_")
                data = '0.0%'
                if labels_information[0] == 'ram':
                    data = str(round(psutil.virtual_memory().percent, 1)) + "%"
                elif labels_information[0] == 'cpu':
                    data = str(round(psutil.cpu_percent(interval=1), 1)) + "%"
                elif labels_information[0] == 'gpu':
                    data = str(round(GPUtil.getGPUs()[0].load*100, 1)) + "%"
                else:
                    data = str(round(GPUtil.getGPUs()[0].memoryUtil * 100, 1)) + "%"
                self.state.append(data)
            mose_position = ','.join(list(map(str, self.mouse.position)))
            self.state.append(mose_position)
            self.sleep(1)
            
class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.index_read()
        self.key_list = [self.button_data[i][-1][0] for i in range(len(self.button_data))]
        self.folder_index = [i for i in range(len(self.key_list)) if self.key_list[i] == 'folder']
        self.system_index = [i for i in range(len(self.key_list)) if self.key_list[i] == 'system']
        
        self.WM_APPCOMMAND = 0x319
        self.hwnd_active = win32gui.GetForegroundWindow()

        self.SW_SHOWNORMAL = 1
        self.shell32 = ctypes.WinDLL('shell32')
        self.shell32.ShellExecuteW.argtypes = w.HWND, w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, w.INT
        self.shell32.ShellExecuteW.restype = w.HINSTANCE

        self.mouse = Controller()
        self.age_mouse_position = [0, 0]

        self.icon_change = [0 for i in range(len(self.button_data))]
        self.display_screen_list = sbc.get_brightness()
        self.key_input = ctypes.windll.user32
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.worker = Worker(self.button_data, self.system_index)
        self.worker.start()
        self.worker.timeout.connect(self.timeout)
        self.initUI()

    def index_read(self):
        f = open("index.txt")
        index = f.read().split("\n")
        f.close()
        self.display_resolution = list(map(int, index[1].split('x')))
        self.play_position = list(map(int, index[3].split('x')))

        self.button_data = []
        button_split = []
        button_data_count = 0

        for i in range(5, len(index)):
            if index[i] == '': continue
            if index[i][0] == "*": continue
            if index[i][0] == "#":
                if i != 5:
                    self.button_data.append(button_split)
                button_split = []
                button_data_count = 0
                continue
            if button_data_count != 4 and button_data_count != 5:
                button_split.append(list(map(int, index[i].split('x'))))
                button_data_count += 1
            elif button_data_count == 5:
                button_split.append([index[i].split('-')[0], '-'.join(index[i].split('-')[1:])])
            else:
                button_split.append(int(index[i]))
                button_data_count += 1
        

    def initUI(self):
        self.background_button = QPushButton(self)
        self.background_button.setStyleSheet('border : 0px solid rgb(0, 0, 0);')
        self.background_button.setFixedSize(1280, 720)
        self.background_button.move(0, 0)
        self.background_button.clicked.connect(self.background_return)
        
        self.none_list = [QPushButton(self) for i in range(14)]
        for i in range(14):
            self.none_list[i].setStyleSheet('border : 5px solid rgb(0, 0, 0); border-radius: 30px;')
            self.none_list[i].setFixedSize(self.button_data[i][0][0], self.button_data[i][0][1])
            self.none_list[i].move(self.button_data[i][2][0], self.button_data[i][2][1])
            
        self.none_list[0].clicked.connect(lambda: self.button(0))
        self.none_list[1].clicked.connect(lambda: self.button(1))
        self.none_list[2].clicked.connect(lambda: self.button(2))
        self.none_list[3].clicked.connect(lambda: self.button(3))
        self.none_list[4].clicked.connect(lambda: self.button(4))
        self.none_list[5].clicked.connect(lambda: self.button(5))
        self.none_list[6].clicked.connect(lambda: self.button(6))
        self.none_list[7].clicked.connect(lambda: self.button(7))
        self.none_list[8].clicked.connect(lambda: self.button(8))
        self.none_list[9].clicked.connect(lambda: self.button(9))
        self.none_list[10].clicked.connect(lambda: self.button(10))
        self.none_list[11].clicked.connect(lambda: self.button(11))
        self.none_list[12].clicked.connect(lambda: self.button(12))
        self.none_list[13].clicked.connect(lambda: self.button(13))
        
        self.dial = QDial(self)
        self.dial.setFixedSize(220, 220)
        self.dial.setRange(0, 100)
        self.dial.setValue(self.display_screen_list[self.icon_change[14]])
        self.dial.move(6, 10)
        self.dial.valueChanged.connect(self.dial_D)

        self.button_list = [QPushButton(self) for i in range(15)]

        for i in range(15):
            self.button_list[i].setFixedSize(self.button_data[i][1][0], self.button_data[i][1][1])
            self.button_list[i].setStyleSheet(f'border-image: url(./icons/{i+1}-0.png);border:0px;')
            self.button_list[i].move(self.button_data[i][3][0], self.button_data[i][3][1])
        self.button_list[0].clicked.connect(lambda: self.button(0))
        self.button_list[1].clicked.connect(lambda: self.button(1))
        self.button_list[2].clicked.connect(lambda: self.button(2))
        self.button_list[3].clicked.connect(lambda: self.button(3))
        self.button_list[4].clicked.connect(lambda: self.button(4))
        self.button_list[5].clicked.connect(lambda: self.button(5))
        self.button_list[6].clicked.connect(lambda: self.button(6))
        self.button_list[7].clicked.connect(lambda: self.button(7))
        self.button_list[8].clicked.connect(lambda: self.button(8))
        self.button_list[9].clicked.connect(lambda: self.button(9))
        self.button_list[10].clicked.connect(lambda: self.button(10))
        self.button_list[11].clicked.connect(lambda: self.button(11))
        self.button_list[12].clicked.connect(lambda: self.button(12))
        self.button_list[13].clicked.connect(lambda: self.button(13))
        self.button_list[14].clicked.connect(lambda: self.button(14))

        self.label_list = []

        for i in range(len(self.folder_index)):
            btn_index = self.folder_index[i]
            self.label_list.append(QLabel(self.button_data[btn_index][-1][1].split('\\')[-1].split('/')[-1], self))
            self.label_list[i].setAlignment(Qt.AlignCenter)
            
            self.label_list[i].move(self.button_data[btn_index][3][0]-(int(abs(self.button_data[btn_index][1][0]-150)/2)),
                                    self.button_data[btn_index][3][1] + (int(abs(self.button_data[btn_index][1][1]-20)/2)))
            self.label_list[i].setFixedSize(150, 20)

            self.font = self.label_list[i].font()
            self.font.setPointSize(16)
            self.font.setBold(True)
            self.label_list[i].setFont(self.font)

        self.system_labels = []

        for i in range(len(self.system_index)):
            btn_index = self.system_index[i]
            labels_information = self.button_data[btn_index][-1][1].split("_")
            self.system_labels.append(QLabel('0.0%', self))
            self.system_labels[i].setAlignment(Qt.AlignCenter)
            self.system_labels[i].move(int(labels_information[2].split('x')[0]), int(labels_information[2].split('x')[1])) 
            self.system_labels[i].setFixedSize(int(labels_information[3].split('x')[0]), int(labels_information[3].split('x')[1]))

            self.font = self.system_labels[i].font()
            self.font.setPointSize(int(labels_information[1]))
            self.font.setBold(True)
            self.system_labels[i].setFont(self.font)

        self.setWindowTitle('touch screen program')
        self.setWindowIcon(QIcon('icon.ico'))
        self.setGeometry(self.play_position[0], self.play_position[1], self.display_resolution[0], self.display_resolution[1])
        self.show()

    @pyqtSlot(list)
    def timeout(self, state):
        for i in range(len(self.system_labels)):
            self.system_labels[i].setText(state[i])
        self.age_mouse_position = list(map(int, state[-1].split(',')))

    def background_return(self):
        self.mouse.position = self.age_mouse_position

    def dial_D(self):
        self.mouse.position = self.age_mouse_position
        sbc.set_brightness(self.dial.value(), display=self.icon_change[14])

    def button(self, input_button_number):
        self.mouse.position = self.age_mouse_position
        input_type = self.button_data[input_button_number][5][0]
        input_data = self.button_data[input_button_number][5][1]

        if self.button_data[input_button_number][4] != 1:
            icon_index = self.button_data[input_button_number][4]
            self.icon_change[input_button_number] += 1

            current_icon = self.icon_change[input_button_number]
            self.button_list[input_button_number].setStyleSheet(f'border-image: url(./icons/{input_button_number+1}-{current_icon}.png);border:0px;')

            if current_icon == icon_index-1:
                self.icon_change[input_button_number] = -1

            if input_button_number == 14:
                self.dial.setValue(self.display_screen_list[current_icon])
        
        if input_type == 'key':
            self.key_input.keybd_event(int(input_data, 16), 0,1,0)
        elif input_type == 'win':
            win32api.SendMessage(self.hwnd_active,
                                 self.WM_APPCOMMAND, None,
                                 int(input_data, 16))
        elif input_type == 'web':
            webbrowser.open_new(url=input_data)
        elif input_type == 'command':
            subprocess.Popen(input_data,
                         shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif input_type == 'folder':
            os.startfile(input_data)
        elif input_type == 'system':
            subprocess.Popen("C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\System Tools\\Task Manager.lnk",
                         shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            print("None")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
