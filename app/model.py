# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import view

import os, sys, time
from os.path import join

import serial
import serial.tools.list_ports

from datetime import datetime, timedelta
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QtWidgets.QMainWindow, view.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # ui variables
        self.setupUi(self)
        self.sceneSize = self.getViewSize(str(self.graphicsView.size()))
        self.canvas = FigureCanvas(self.waveForm())
        self.graphicscene = QtWidgets.QGraphicsScene()
        self.graphicscene.setSceneRect(0.0, 0.0, self.sceneSize[0], self.sceneSize[1])
        self.graphicscene.addWidget(self.canvas)
        self.graphicsView.setScene(self.graphicscene)
        #print(self.getViewSize(str(self.graphicsView.size())))

        self.COMPortList = {}
        self.comboBox.addItems(self.listPort())
        
        self.t = 0  # time step for sin wave
        
        #self.Timer(self.test_count)
        #self.run()
    
    ## Basic Operation
    # get graphicView's size (width, height)
    def getViewSize(self, sizeStr):
        sizeRange = sizeStr.split("(")[1][0:-1]
        sizeRange = list(map(int, sizeRange.split(",")))
        return sizeRange

    ## Serial Port Setting
    # clear texts in console
    def clearConsole(self):
        # for windows
        if os.name == 'nt':
            _ = os.system('cls')
        # for mac and linux
        else:
            _ = os.system('clear')

    # return list of available COM port
    def listPort(self):
        ports = map(str, serial.tools.list_ports.comports())
        if ports:
            for p in ports:
                #print(p)
                self.COMPortList[p.split(' - ')[0]] = p
            return self.COMPortList.keys()
        else:
            return [""]

    # connet port
    def connectPort(self, com_port, baud_rate, time_out):
        port_name = com_port.split(" ")[0]
        ser = serial.Serial(port_name, baud_rate, timeout=time_out)   # set the serial connection
        return ser

    ## Plot Setting
    # initial figure
    def waveForm(self):
        fig = plt.figure(figsize=(self.sceneSize[0]/100, self.sceneSize[1]/100), dpi=100)
        ax = plt.axes(xlim=(0, 30), ylim=(-2, 4))
        ax.set_xlabel('timepoint (sec)')
        ax.set_ylabel('airflow rate (mL/min)')
        line, = ax.plot([], [])
        x = np.linspace(0, 30, 300)
        y = np.zeros(300)
        line.set_data(x, y)
        plt.close()
        return fig

    def count(self):
        #self.t = self.t + 5
        self.canvas = FigureCanvas(self.waveForm())
        self.graphicscene.clear()
        self.graphicscene.addWidget(self.canvas)

    # function test - sine wave
    def sinWave(self, i=0):
        fig = plt.figure(figsize=(self.sceneSize[0]/100, self.sceneSize[1]/100), dpi=100)
        ax = plt.axes(xlim=(0, 2), ylim=(-2, 2), xlabel='timepoint', ylabel='airflow rate (mL/min)')
        line, = ax.plot([], [])
        line.set_data([], [])
        x = np.linspace(0, 2, 100)
        y = np.sin(5 * np.pi * (x - 0.01*i))
        line.set_data(x, y)
        plt.close()
        return fig

    # function test - counter
    def test_count(self):
        self.t = self.t + 5
        self.canvas = FigureCanvas(self.sinWave(self.t))
        self.graphicscene.clear()
        self.graphicscene.addWidget(self.canvas)

    ## Thread setting
    def Timer(self, func, t=50):
        timer = QtCore.QTimer()
        timer.timeout.connect(func)
        timer.start(t)

    def run(self):
        self.thread_figurecanvas = QtCore.QThread()
        self.thread_figurecanvas.run = self.test_count
        self.thread_figurecanvas.start()

if __name__ == '__main__':
        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow()
        window.show()

        timer = QtCore.QTimer()
        timer.timeout.connect(window.count)
        timer.start(50)

        sys.exit(app.exec_())
'''

# clear the screen





## recording setting


# ask the directory to save the data
def ask_directory():
    root = tk.Tk()
    root.withdraw()
    folder = askdirectory(parent=root, initialdir='d:')
    return folder

# acquire and parse data
def get_data(ser):
    data_raw = ser.readline()
    try:
        data = float(data_raw.decode().strip())
        now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print("{} -> {}".format(now, data))
        return now, data
    except:
        return datetime.now().strftime('%H:%M:%S.%f')[:-3]
    

# set record information
def set_rec_info():
    rec_time = int(input("Enter the recording time (sec): "))
    sample_id = str(input("Enter the sample ID: ")).replace(" ", "_")
    rectime_head = "{}_time".format(sample_id)
    if rec_time > 0:
        time_delta = timedelta(seconds=rec_time)
        return rec_time, time_delta, sample_id, rectime_head  # return time_delta
    else:
        print("Recording time should be positive. Try next time.")
        return 0, timedelta(seconds=0), sample_id, "", ""

# set start flag
def set_start_flag(start, time_delta, end_rec):
    if start:
        return start, end_rec
    else:
        if time_delta != timedelta(seconds=0):  # skip initial condition
            if datetime.now() > end_rec:        # don't start another recording while one is running
                end_rec = datetime.now() + time_delta
                #print(end_rec)
                return True, end_rec         # return start flag and end_rec time
            else:
                return False, datetime.now()
        else:
            return False, datetime.now()

# prompt the user input for file name
def get_fname(folder):
    while True:
        fName = input("Enter the file name: ")
        if fName:
            if fName.split('.')[-1] != "csv":
                if fName.endswith('.'):
                    fName = "{}csv".format(fName)
                else:
                    fName = "{}.csv".format(fName)
            else:
                fName = fName
            return join(folder, fName)
        else:
            input("File name cannot be empty\nPress Enter to continue...")
            continue

# count max length of a list of lists
def find_maxlen(lists):
    max_length = 0
    for l in lists:
        length = len(l)
        if length > max_length:
            max_length = length
    return max_length

# making every list in all_record has same length by filling na
def fill_na(all_record):
    max_length = find_maxlen(all_record.values())   # find the length of the longest list
    for key, value in all_record.items():
        n = max_length - len(value)
        if n:
            na_array = np.empty(n)
            na_array.fill(np.nan)
            all_record[key] = value.extend(na_array)

# save record
def save_record(all_record, folder):
    file_name = get_fname(folder)
    fill_na(all_record)
    df = pd.DataFrame(all_record)
    df.to_csv(file_name, index=False)

# reset the start flag and records
def reset():
    return False, [], []



def makeFigure():
    fig = Figure(figsize=(6, 2.5), dpi=100, tight_layout=True)
    ax = fig.add_subplot(111)
    ax.set_xlabel('timepoint', fontsize=10)
    ax.set_ylabel('airflow rate (mL/min)', fontsize=10)
    ax.set_xlim(0, 60)
    ax.set_ylim(-15, 40)
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    line, = ax.plot([], [])

    return fig, ax, line
'''

    