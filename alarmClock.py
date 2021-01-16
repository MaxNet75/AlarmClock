#!/usr/bin/python3

import tkinter
import tkinter.ttk
import datetime
import time
import os
import subprocess
import pickle
import urllib.request
import requests
import configparser
from math import *

#
# RADIO
#
radioList = {
    '1': {'name': 'RTL 2', 	'image': 'imageRTL2', 		'item': 'ParentsRoom_GoogleHome_Stream_RTL2'},
    '2': {'name': 'Europe 1',	'image': 'imageEUROPE1',		'item': 'ParentsRoom_GoogleHome_Stream_EUROPE1'},
    '3': {'name': 'Fun Radio',	'image': 'imageFUNRADIO',		'item': 'ParentsRoom_GoogleHome_Stream_FUN'},
    '4': {'name': 'Oui FM',	'image': 'imageOUIFM',		'item': 'ParentsRoom_GoogleHome_Stream_OUIFM'},
    '5': {'name': 'Nova',	'image': 'imageNOVA',		'item': 'ParentsRoom_GoogleHome_Stream_NOVA'},
}

radioObject=None

# Default config values
config = configparser.ConfigParser()
config['DISPLAY'] = {}
config['DISPLAY']['brightness'] = '20'
config['DISPLAY']['brightness_min'] = '10'
config['DISPLAY']['brightness_max'] = '30'
config['SOUND'] = {}
config['SOUND']['volume'] = '50'
config['ALARM'] = {}
config['ALARM']['status'] = '1'
config['ALARM']['alarm'] = '430'
config['BEDROOM1'] = {}
config['BEDROOM1']['status'] = '1'
config['BEDROOM1']['offset'] = '10'
config['BEDROOM2'] = {}
config['BEDROOM2']['status'] = '1'
config['BEDROOM2']['offset'] = '10'

def init():
    global config

    if os.path.isfile('alarmClock.ini'):
        config = readConfig()

    setVolume(config['SOUND']['volume'])
    setBrightness(config['DISPLAY']['brightness'])
    setBedroom1Status(config['BEDROOM1']['status'])
    setBedroom1Offset(config['BEDROOM1']['offset'])
    setAlarmStatus(config['ALARM']['status'])
    setAlarm(config['ALARM']['alarm'])
    setBedroom2Status(config['BEDROOM2']['status'])
    setBedroom2Offset(config['BEDROOM2']['Offset'])

    # Execute init commands
    os.system('sudo xset s off')
    os.system('sudo xset -dpms')
    os.system('sudo xset s noblank')

#
# Config file
#
def writeConfig(config):
	file = open('alarmClock.ini', 'w')
	config.write(file)
	file.close()

def readConfig():
	file = open('alarmClock.ini', 'r')
	config = configparser.ConfigParser()
	config.read_file(file)
	file.close()
	return config

#
# Volume
#
def getVolume():
	res = requests.get('http://192.168.0.150:8080/rest/items/ParentsRoom_GoogleHome_Volume')
	return int(res.json()['state'])

def setVolume(volume):
	res = requests.post('http://192.168.0.150:8080/rest/items/ParentsRoom_GoogleHome_Volume', data=str(volume))
	
def increaseVolume():
	setVolume(getVolume()+1)

def decreaseVolume():
	setVolume(getVolume()-1)

#
# Clock
#
def getTimeInMinutes():
	return int(time.strftime("%H")) * 60 + int(time.strftime("%M"))

def clockUpdate(label):
	label.set(time.strftime("%H:%M"))
	root.after(1000, lambda:clockUpdate(label))

#
# Brightness
#
def getBrightness():
	brightness = int(subprocess.check_output(['cat /sys/class/backlight/rpi_backlight/brightness'], shell=True))
	return brightness

def setBrightness(brightness):
	os.system('sudo bash -c "echo '+str(brightness)+' > /sys/class/backlight/rpi_backlight/brightness"')

def increaseBrightness():
	setBrightness(getBrightness()+1)

def decreaseBrightness():
	setBrightness(getBrightness()-1)

#
# Alarm
#
def getAlarmStatus():
	global alarmStatusVariable
	return alarmStatusVariable.get()

def setAlarmStatus(status):
	global alarmStatusVariable
	alarmStatusVariable.set(status)

def getAlarmInMinutes():
	global alarmLabelVariable
	array = alarmLabelVariable.get().split(':')
	return int(array[0]) * 60 + int(array[1])

def setAlarm(minutes):
	global alarmLabelVariable
	alarmLabelVariable.set(str(floor(int(minutes) / 60)).zfill(2)+':'+str(int(minutes) % 60).zfill(2))

def increaseAlarmHours():
	if getAlarmInMinutes() < 1380:
		setAlarm(getAlarmInMinutes() + 60)

def decreaseAlarmHours():
	if getAlarmInMinutes() > 59:
		setAlarm(getAlarmInMinutes() - 60)

def increaseAlarmMinutes():
	if getAlarmInMinutes() < 1439:
		setAlarm(getAlarmInMinutes() + 1)

def decreaseAlarmMinutes():
	if getAlarmInMinutes() > 0:
		setAlarm(getAlarmInMinutes() - 1)

def alarm():
	if getAlarmStatus() == 1 and getTimeInMinutes() == getAlarmInMinutes():
		turnOnRadio(radioSelect.get())
		root.after(60000, lambda:alarm())
	else:
		root.after(1000, lambda:alarm())

#
# Bedroom 1
#
def getBedroom1Status():
	global bedroom1StatusVariable
	return bedroom1StatusVariable.get()

def setBedroom1Status(status):
	global bedroom1StatusVariable
	bedroom1StatusVariable.set(status)

def getBedroom1Offset():
	global bedroom1OffsetVariable
	return int(bedroom1OffsetVariable.get())

def setBedroom1Offset(minutes):
	global bedroom1OffsetVariable
	bedroom1OffsetVariable.set(str(minutes))

def openBedroom1Shutter():
    res = requests.post('http://192.168.0.150:8080/rest/items/ParentsRoom_Rollershutter_Blinds', data='UP')

def stopBedroomm1Shutter():
    res = requests.post('http://192.168.0.150:8080/rest/items/ParentsRoom_Rollershutter_Blinds', data='STOP')

def closeBedroom1Shutter():
    res = requests.post('http://192.168.0.150:8080/rest/items/ParentsRoom_Rollershutter_Blinds', data='DOWN')


def increaseBedroom1Offset():
	if int(getBedroom1Offset()) < 30:
		setBedroom1Offset(int(getBedroom1Offset()) + 1)

def decreaseBedroom1Offset():
	if int(getBedroom1Offset()) > 0:
		setBedroom1Offset(int(getBedroom1Offset()) - 1)

def bedroom1():
	if getBedroom1Status() == 1 and getTimeInMinutes() == getAlarmInMinutes() + getBedroom1Offset():
		openBedroom1Shutter()
		root.after(60000, lambda:bedroom1())
	else:
		root.after(1000, lambda:bedroom1())

#
# Bedroom 2
#
def getBedroom2Status():
	global bedroom2StatusVariable
	return bedroom2StatusVariable.get()

def setBedroom2Status(status):
	global bedroom2StatusVariable
	bedroom2StatusVariable.set(status)

def getBedroom2Offset():
	global bedroom2OffsetVariable
	return int(bedroom2OffsetVariable.get())

def setBedroom2Offset(minutes):
	global bedroom2OffsetVariable
	bedroom2OffsetVariable.set(str(minutes))

def openBedroom2Shutter():
    res = requests.post('http://192.168.0.150:8080/rest/items/ChildrensRoom_Rollershutter_Blinds', data='UP')

def stopBedroomm2Shutter():
    res = requests.post('http://192.168.0.150:8080/rest/items/ChildrensRoom_Rollershutter_Blinds', data='STOP')

def closeBedroom2Shutter():
    res = requests.post('http://192.168.0.150:8080/rest/items/ChildrensRoom_Rollershutter_Blinds', data='DOWN')


def increaseBedroom2Offset():
	if int(getBedroom2Offset()) < 30:
		setBedroom2Offset(getBedroom2Offset() + 1)

def decreaseBedroom2Offset():
	if int(getBedroom2Offset()) > 0:
		setBedroom2Offset(getBedroom2Offset() - 1)

def bedroom2():
	if getBedroom2Status() == 1 and getTimeInMinutes() == getAlarmInMinutes() + getBedroom2Offset():
		openBedroom2Shutter()
		root.after(60000, lambda:bedroom2())
	else:
		root.after(1000, lambda:bedroom2())

#
#
#
def exit():
	global radioObject
	if radioObject is not None:
		radioObject.terminate()
		radioObject=None
	os.system('sudo xset s on')
	os.system('sudo xset +dpms')
	os.system('sudo xset s blank')

	config['SOUND']['volume'] = str(getVolume())
	config['DISPLAY']['brightness'] = str(getBrightness())
	config['BEDROOM1']['status'] = str(getBedroom1Status())
	config['BEDROOM1']['offset'] = str(getBedroom1Offset())
	config['ALARM']['status'] = str(getAlarmStatus())
	config['ALARM']['alarm'] = str(getAlarmInMinutes())
	config['BEDROOM2']['status'] = str(getBedroom2Status())
	config['BEDROOM2']['Offset'] = str(getBedroom2Offset())
	writeConfig(config)
	setBrightness(40)
	root.destroy()

def showMessage(text):
	message=tkinter.Message(root, text=text)
	message.pack()
	message.place(anchor="center", x=screenWidth/2, y=screenHeight/2, width=200, height=100)
	root.after(5000, lambda:message.destroy())

def turnOnRadio(radioId):
	res = requests.post('http://192.168.0.150:8080/rest/items/'+radioList[str(radioId)]['item'], data='ON')
	
def turnOffRadio(radioId):
	res = requests.post('http://192.168.0.150:8080/rest/items/'+radioList[str(radioId)]['item'], data='OFF')

root=tkinter.Tk()

screenWidth=root.winfo_screenwidth()
screenHeight=root.winfo_screenheight()

clockLabelVariable = tkinter.StringVar()
clockLabelVariable.set(time.strftime("%H:%M"))

labelTimeText=tkinter.StringVar()
labelTimeText.set('00:00')

radioSelect=tkinter.IntVar()
radioSelect.set(1)

bedroom1StatusVariable = tkinter.IntVar()
bedroom1OffsetVariable = tkinter.IntVar()

alarmStatusVariable = tkinter.IntVar()
alarmLabelVariable = tkinter.StringVar()

bedroom2StatusVariable = tkinter.IntVar()
bedroom2OffsetVariable = tkinter.IntVar()

init()
alarm()
bedroom1()
bedroom2()

root.overrideredirect(1)
root.geometry("%dx%d+0+0" % (screenWidth, screenHeight))
root.wm_title("Alarm clock")
root.configure(bg="black")

#
# IMAGES
#
imageEnabled = tkinter.PhotoImage(file='enabled.png')
imageDisabled = tkinter.PhotoImage(file='disabled.png')
imageRTL2 = tkinter.PhotoImage(file='rtl2.png')

#
# VOLUME
#
volumeFrame = tkinter.LabelFrame(root, text='Volume', bg = 'black', fg = 'red', font=('arial', 15))
volumeFrame.pack()
volumeFrame.place(anchor = 'nw', x = 0, y = 0, width = screenWidth / 6, height = screenHeight / 3)
volumeFrame.update()

volumeIncreaseButton = tkinter.Button(volumeFrame, text = '+', command = lambda:increaseVolume())
volumeIncreaseButton.pack()
volumeIncreaseButton.place(anchor = 'center', x = volumeFrame.winfo_width() / 2, y = volumeFrame.winfo_height() / 6, width = 50, height = 30)

volumeDecreaseButton = tkinter.Button(volumeFrame, text='-', command=lambda:decreaseVolume())
volumeDecreaseButton.pack()
volumeDecreaseButton.place(anchor = 'center', x = volumeFrame.winfo_width() / 2, y = volumeFrame.winfo_height() / 6 * 4, width = 50, height = 30)

#
# CLOCK
#
clockFrame = tkinter.LabelFrame(root, text='Clock', bg = 'black', fg = 'red', font=('arial', 15))
clockFrame.pack()
clockFrame.place(anchor = 'n', x = screenWidth / 2, y = 0, width = screenWidth / 6 * 4, height = screenHeight / 3)
clockFrame.update()

clockLabel = tkinter.Label(clockFrame, textvariable=clockLabelVariable, bg="black", fg="red", font=("arial", 90))
clockLabel.pack()
clockLabel.place(anchor = 'center', x = clockFrame.winfo_width() / 2, y = clockFrame.winfo_height() / 5 * 2, width = 350, height = 100)
clockUpdate(clockLabelVariable)

#
# BRIGHTNESS
#
brightnessFrame = tkinter.LabelFrame(root, text='Brightness', bg = 'black', fg = 'red', font=('arial', 15))
brightnessFrame.pack()
brightnessFrame.place(anchor = 'ne', x = screenWidth, y = 0, width = screenWidth / 6, height = screenHeight / 3)
brightnessFrame.update()

brightnessIncreaseButton = tkinter.Button(brightnessFrame, text="+", command=lambda:increaseBrightness())
brightnessIncreaseButton.pack()
brightnessIncreaseButton.place(anchor = 'center', x = brightnessFrame.winfo_width() / 2, y = brightnessFrame.winfo_height() / 6, width = 50, height = 30)

brightnessDecreaseButton = tkinter.Button(brightnessFrame, text = '-', command=lambda:decreaseBrightness())
brightnessDecreaseButton.pack()
brightnessDecreaseButton.place(anchor = 'center', x = brightnessFrame.winfo_width() / 2, y = brightnessFrame.winfo_height() / 6 * 4, width = 50, height = 30)

#
# RADIO LIST
#
radioFrame = tkinter.LabelFrame(root, text='Radio', bg = 'black', fg = 'red', font=('arial', 15))
radioFrame.pack()
radioFrame.place(anchor = 'center', x = screenWidth / 2, y = screenHeight / 2, width = screenWidth, height = screenHeight / 3)
radioFrame.update()

for radioKey, radioValue in radioList.items():
	radiobuttonRadio=tkinter.Radiobutton(radioFrame, anchor="center", image=imageRTL2, text=radioValue['name'], variable=radioSelect, value=radioKey, indicatoron='false')
	radiobuttonRadio.pack()
	radiobuttonRadio.place(anchor = 'center', x = radioFrame.winfo_width() / (len(radioList) + 1) * int(radioKey), y = radioFrame.winfo_height() / 5, width = 300, height = 60)

#
# ON / OFF
#
buttonTurnOnRadio = tkinter.Button(root, text="On", command=lambda:turnOnRadio(radioSelect.get()))
buttonTurnOnRadio.pack()
buttonTurnOnRadio.place(anchor="center", x=screenWidth/2+50, y=screenHeight/2+50, width=50, height=30)

buttonTurnOffRadio = tkinter.Button(root, text="Off", command=lambda:turnOffRadio(radioSelect.get()))
buttonTurnOffRadio.pack()
buttonTurnOffRadio.place(anchor = 'center', x = screenWidth / 2 - 50, y = screenHeight / 2 + 50, width = 50, height = 30)

#
# Bedroom 1
#
bedroom1Status = tkinter.Checkbutton(image=imageDisabled, selectimage=imageEnabled, text='Bedroom 1', variable=bedroom1StatusVariable, indicatoron='false', selectcolor='black', bg='black', activeforeground='black', activebackground='black', highlightbackground='black', fg='red',  font=('arial', 15), bd=0, highlightthickness=0, highlightcolor='black')

bedroom1Frame = tkinter.LabelFrame(root, labelwidget=bedroom1Status, bg = 'black', fg = 'red')
bedroom1Frame.pack()
bedroom1Frame.place(anchor = 'sw', x = 0, y = screenHeight, width = screenWidth / 3, height = screenHeight / 3)
bedroom1Frame.update()

bedRoom1ButtonOpen = tkinter.Button(bedroom1Frame, text='⇧', command = openBedroom1Shutter)
bedRoom1ButtonOpen.pack()
bedRoom1ButtonOpen.place(anchor = 'center', x = bedroom1Frame.winfo_width() / 8, y = (bedroom1Frame.winfo_height() / 3) - 30, width = 30, height = 30)

bedRoom1ButtonStop = tkinter.Button(bedroom1Frame, text='☐', command = stopBedroomm1Shutter)
bedRoom1ButtonStop.pack()
bedRoom1ButtonStop.place(anchor = 'center', x = bedroom1Frame.winfo_width() / 8, y = (bedroom1Frame.winfo_height() / 2) - 15, width = 30, height = 30)

bedRoom1ButtonClose = tkinter.Button(bedroom1Frame, text='⇩', command = closeBedroom1Shutter)
bedRoom1ButtonClose.pack()
bedRoom1ButtonClose.place(anchor = 'center', x = bedroom1Frame.winfo_width() / 8, y = bedroom1Frame.winfo_height() / 3 * 2, width = 30, height = 30)

bedroom1Offset = tkinter.Label(bedroom1Frame, textvariable=bedroom1OffsetVariable, bg="black", fg="red", font=('arial', 30))
bedroom1Offset.pack()
bedroom1Offset.place(anchor = "center", x = bedroom1Frame.winfo_width() / 2, y = bedroom1Frame.winfo_height() / 2 - 15)

bedroom1OffsetIncrease = tkinter.Button(bedroom1Frame, text='+', command = increaseBedroom1Offset)
bedroom1OffsetIncrease.pack()
bedroom1OffsetIncrease.place(anchor = 'center', x = bedroom1Frame.winfo_width() / 8 * 7, y = (bedroom1Frame.winfo_height() / 3) - 30, width = 30, height = 30)

bedroom1OffsetDecrease = tkinter.Button(bedroom1Frame, text='-', command = decreaseBedroom1Offset)
bedroom1OffsetDecrease.pack()
bedroom1OffsetDecrease.place(anchor = 'center', x = bedroom1Frame.winfo_width() / 8 * 7, y = bedroom1Frame.winfo_height() / 3 * 2, width = 30, height = 30)

#
# ALARM
#
alarmStatus = tkinter.Checkbutton(image=imageDisabled, selectimage=imageEnabled, text='Alarm', variable=alarmStatusVariable, indicatoron='false', selectcolor='black', bg='black', activeforeground='black', activebackground='black', highlightbackground='black', fg='red',  font=('arial', 15), bd=0, highlightthickness=0, highlightcolor='black')

alarmFrame = tkinter.LabelFrame(root, labelwidget=alarmStatus, bg='black', fg='red')
alarmFrame.pack()
alarmFrame.place(anchor = 's', x = screenWidth / 2, y = screenHeight, width = screenWidth / 3, height = screenHeight / 3)
alarmFrame.update()

alarmButtonIncreaseAlarmHours = tkinter.Button(alarmFrame, text='+', command=increaseAlarmHours)
alarmButtonIncreaseAlarmHours.pack()
alarmButtonIncreaseAlarmHours.place(anchor = 'center', x = alarmFrame.winfo_width() / 8, y = (alarmFrame.winfo_height() / 3) - 30, width = 30, height = 30)

buttonDecreaseAlarmHours = tkinter.Button(alarmFrame, text="-", command=decreaseAlarmHours)
buttonDecreaseAlarmHours.pack()
buttonDecreaseAlarmHours.place(anchor="center", x = alarmFrame.winfo_width() / 8, y = alarmFrame.winfo_height() / 3 * 2, width = 30, height = 30)

alarmLabel = tkinter.Label(alarmFrame, textvariable=alarmLabelVariable, bg="black", fg="red", font=('arial', 30))
alarmLabel.pack()
alarmLabel.place(anchor = "center", x=125, y=65)

buttonIncreaseAlarmMinutes=tkinter.Button(alarmFrame, text='+', command=increaseAlarmMinutes)
buttonIncreaseAlarmMinutes.pack()
buttonIncreaseAlarmMinutes.place(anchor="center", x = alarmFrame.winfo_width() / 8 * 7, y = (alarmFrame.winfo_height() / 3) - 30, width = 30, height = 30)

buttonDecreaseAlarmMinutes=tkinter.Button(alarmFrame, text="-", command=decreaseAlarmMinutes)
buttonDecreaseAlarmMinutes.pack()
buttonDecreaseAlarmMinutes.place(anchor="center", x = alarmFrame.winfo_width() / 8 * 7, y = alarmFrame.winfo_height() / 3 * 2, width = 30, height = 30)

#
# Bedroom 2
#
bedroom2Status = tkinter.Checkbutton(image=imageDisabled, selectimage=imageEnabled, text='Bedroom 2', variable=bedroom2StatusVariable, indicatoron='false', selectcolor='black', bg='black', activeforeground='black', activebackground='black', highlightbackground='black', fg='red',  font=('arial', 15), bd=0, highlightthickness=0, highlightcolor='black')

bedroom2Frame = tkinter.LabelFrame(root, labelwidget=bedroom2Status, bg = 'black', fg = 'red')
bedroom2Frame.pack()
bedroom2Frame.place(anchor = 'se', x = screenWidth, y = screenHeight, width = screenWidth / 3, height = screenHeight / 3)
bedroom2Frame.update()

bedRoom2ButtonOpen = tkinter.Button(bedroom2Frame, text='⇧', command = openBedroom2Shutter)
bedRoom2ButtonOpen.pack()
bedRoom2ButtonOpen.place(anchor = 'center', x = bedroom2Frame.winfo_width() / 8, y = (bedroom2Frame.winfo_height() / 3) - 30, width = 30, height = 30)

bedRoom2ButtonStop = tkinter.Button(bedroom2Frame, text='☐', command = stopBedroomm2Shutter)
bedRoom2ButtonStop.pack()
bedRoom2ButtonStop.place(anchor = 'center', x = bedroom2Frame.winfo_width() / 8, y = (bedroom2Frame.winfo_height() / 2) - 15, width = 30, height = 30)

bedRoom2ButtonClose = tkinter.Button(bedroom2Frame, text='⇩', command = closeBedroom2Shutter)
bedRoom2ButtonClose.pack()
bedRoom2ButtonClose.place(anchor = 'center', x = bedroom2Frame.winfo_width() / 8, y = bedroom2Frame.winfo_height() / 3 * 2, width = 30, height = 30)

bedroom2Offset = tkinter.Label(bedroom2Frame, textvariable=bedroom2OffsetVariable, bg="black", fg="red", font=('arial', 30))
bedroom2Offset.pack()
bedroom2Offset.place(anchor = "center", x = bedroom2Frame.winfo_width() / 2, y = bedroom2Frame.winfo_height() / 2 - 15)

bedroom2OffsetIncrease = tkinter.Button(bedroom2Frame, text='+', command = increaseBedroom2Offset)
bedroom2OffsetIncrease.pack()
bedroom2OffsetIncrease.place(anchor = 'center', x = bedroom2Frame.winfo_width() / 8 * 7, y = (bedroom2Frame.winfo_height() / 3) - 30, width = 30, height = 30)

bedroom2OffsetDecrease = tkinter.Button(bedroom2Frame, text='-', command = decreaseBedroom2Offset)
bedroom2OffsetDecrease.pack()
bedroom2OffsetDecrease.place(anchor = 'center', x = bedroom2Frame.winfo_width() / 8 * 7, y = bedroom2Frame.winfo_height() / 3 * 2, width = 30, height = 30)

#
# EXIT
#
buttonExit=tkinter.Button(root, text="Exit", command=exit)
buttonExit.pack()
buttonExit.place(anchor="center", x=screenWidth-40, y=screenHeight/2+50, width=50, height=30)

root.mainloop()
