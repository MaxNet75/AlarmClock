#!/usr/bin/python3

import tkinter
import tkinter.ttk
import datetime
import time
import os
import subprocess
import pickle

radioList={
	'1': {'name': 'RTL 2', 'url': 'http://streaming.radio.rtl2.fr/rtl2-1-48-192'},
	'2': {'name': 'Europe 1', 'url': 'http://mp3lg4.tdf-cdn.com/9240/lag_180945.mp3'},
	'3': {'name': 'Fun', 'url': 'http://streaming.radio.funradio.fr/fun-1-48-192'},
	'4': {'name': 'Oui FM', 'url': 'http://ouifm.ice.infomaniak.ch/ouifm-high.mp3'},
	'5': {'id': 5, 'name': 'Nova', 'url': 'http://novazz.ice.infomaniak.ch/novazz-128.mp3'},
}

radioObject=None

def init():
	# Create data file if not exist
	if not os.path.isfile('test'):
		file=open('test', 'wb')
		pickle.dump(20, file)		# Brightness
		pickle.dump(50, file)		# Volume
		pickle.dump([8, 0], file)	# AlarmClock [Hours, Minutes]
		file.close()
	# Read data file
	file=open('test', 'rb')
	setBrightness(pickle.load(file))
	setVolume(pickle.load(file))
	setAlarmClock(pickle.load(file))
	file.close()
	# Execute init commands
	os.system('sudo rfkill block all')
	os.system('sudo xset s off')
	os.system('sudo xset -dpms')
	os.system('sudo xset s noblank')

def timeUpdate(label):
	labelTimeText.set(time.strftime("%H:%M"))
	root.after(1000, lambda:timeUpdate(label))

def alarm():
	if time.strftime("%H:%M") == alarmClockSelect.get():
		turnOnRadio(radioSelect.get())
		root.after(60000, lambda:alarm())
	else:
		root.after(1000, lambda:alarm())

def getAlarmClock():
	global alarmClockSelect
	return alarmClockSelect.get().split(':')

def setAlarmClock(time):
	global alarmClockSelect
	alarmClockSelect.set(str(time[0]).zfill(2)+':'+str(time[1]).zfill(2))

def getVolume():
	volume=int(subprocess.check_output(['amixer get PCM |grep -oE [0-9]+% |grep -oE [0-9]+'], shell=True))
	return volume

def setVolume(volume):
	os.system('amixer set PCM -- '+str(volume)+'% > /dev/null 2>&1')

def getBrightness():
	brightness=int(subprocess.check_output(['cat /sys/class/backlight/rpi_backlight/brightness'], shell=True))
	return brightness

def setBrightness(brightness):
	os.system('sudo bash -c "echo '+str(brightness)+' > /sys/class/backlight/rpi_backlight/brightness"')

def increaseVolume():
	setVolume(getVolume()+1)

def decreaseVolume():
	setVolume(getVolume()-1)

def increaseBrightness():
	setBrightness(getBrightness()+1)

def decreaseBrightness():
	setBrightness(getBrightness()-1)

def increaseAlarmHours():
	global alarmClockSelect
	alarmClockSelectList=alarmClockSelect.get().split(":")
	if int(alarmClockSelectList[0]) < 23:
		alarmClockSelect.set(str(int(alarmClockSelectList[0])+1).zfill(2)+':'+alarmClockSelectList[1])

def decreaseAlarmHours():
	global alarmClockSelect
	alarmClockSelectList=alarmClockSelect.get().split(':')
	if int(alarmClockSelectList[0]) > 0:
		alarmClockSelect.set(str(int(alarmClockSelectList[0])-1).zfill(2)+':'+alarmClockSelectList[1])

def increaseAlarmMinutes():
	global alarmClockSelect
	alarmClockSelectList=alarmClockSelect.get().split(':')
	if int(alarmClockSelectList[1]) < 59:
		alarmClockSelect.set(alarmClockSelectList[0]+':'+str(int(alarmClockSelectList[1])+1).zfill(2))

def decreaseAlarmMinutes():
	global alarmClockSelect
	alarmClockSelectList=alarmClockSelect.get().split(':')
	if int(alarmClockSelectList[1]) > 0:
		alarmClockSelect.set(alarmClockSelectList[0]+':'+str(int(alarmClockSelectList[1])-1).zfill(2))

def exit():
	global radioObject, alarmClockSelect
	if radioObject is not None:
		radioObject.terminate()
		radioObject=None
	os.system('sudo xset s on')
	os.system('sudo xset +dpms')
	os.system('sudo xset s blank')
	os.system('sudo rfkill unblock all')
	file=open('test', 'wb')
	pickle.dump(getBrightness(), file)
	pickle.dump(getVolume(), file)
	pickle.dump(getAlarmClock(), file)
	file.close()
	setBrightness(40)
	root.destroy()

def ping():
	for cpt in range(1, 10):
		result=os.system('ping -c 1 google.fr >/dev/null 2>&1')
		if result == 0:
			return True
		time.sleep(1)
	return False

def showMessage(text):
	message=tkinter.Message(root, text=text)
	message.pack()
	message.place(anchor="center", x=screenWidth/2, y=screenHeight/2, width=200, height=100)
	root.after(5000, lambda:message.destroy())

def turnOnRadio(radioId):
	global radioObject
	if radioObject is not None:
		radioObject.terminate()
	os.system('sudo rfkill unblock all')
	if ping():
		radioObject=subprocess.Popen(['mplayer', radioList[str(radioId)]['url']], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	else:
		showMessage('Pas de connexion internet !')

def turnOffRadio():
	global radioObject
	if radioObject is not None:
		radioObject.terminate()
		radioObject=None
		os.system('sudo rfkill block all')

root=tkinter.Tk()

screenWidth=root.winfo_screenwidth()
screenHeight=root.winfo_screenheight()

labelTimeText=tkinter.StringVar()
labelTimeText.set('00:00')

radioSelect=tkinter.IntVar()
radioSelect.set(1)

alarmClockSelect=tkinter.StringVar()
#alarmClockSelect.set(alarmClock)

init()

alarm()

root.overrideredirect(1)
root.geometry("%dx%d+0+0" % (screenWidth, screenHeight))
root.wm_title("Alarm clock")
root.configure(bg="black")

labelTime=tkinter.Label(root, textvariable=labelTimeText, bg="black", fg="red", font=("arial", 90))
labelTime.pack()
labelTime.place(anchor="center", x=screenWidth/2, y=screenHeight/4, width=350, height=100)
timeUpdate(labelTimeText)

buttonIncreaseVolume=tkinter.Button(root, text="+", command=lambda:increaseVolume())
buttonIncreaseVolume.pack()
buttonIncreaseVolume.place(anchor="center", x=50, y=100, width=50, height=30)

buttonDecreaseVolume=tkinter.Button(root, text="-", command=lambda:decreaseVolume())
buttonDecreaseVolume.pack()
buttonDecreaseVolume.place(anchor="center", x=50, y=150, width=50, height=30)

buttonIncreaseBrightness=tkinter.Button(root, text="+", command=lambda:increaseBrightness())
buttonIncreaseBrightness.pack()
buttonIncreaseBrightness.place(anchor="center", x=screenWidth-50, y=100, width=50, height=30)

buttonDecreaseBrightness=tkinter.Button(root, text="-", command=lambda:decreaseBrightness())
buttonDecreaseBrightness.pack()
buttonDecreaseBrightness.place(anchor="center", x=screenWidth-50, y=150, width=50, height=30)

buttonTurnOnRadio=tkinter.Button(root, text="On", command=lambda:turnOnRadio(radioSelect.get()))
buttonTurnOnRadio.pack()
buttonTurnOnRadio.place(anchor="center", x=screenWidth/2+50, y=screenHeight/2+50, width=50, height=30)

buttonTurnOffRadio=tkinter.Button(root, text="Off", command=turnOffRadio)
buttonTurnOffRadio.pack()
buttonTurnOffRadio.place(anchor="center", x=screenWidth/2-50, y=screenHeight/2+50, width=50, height=30)

for radioKey, radioValue in radioList.items():
	radiobuttonRadio=tkinter.Radiobutton(root, anchor="w", text=radioValue['name'], variable=radioSelect, value=radioKey)
	radiobuttonRadio.pack()
	radiobuttonRadio.place(anchor="center", x=screenWidth/(len(radioList)+1)*int(radioKey), y=screenHeight/2, width=100, height=30)

buttonIncreaseAlarmHours=tkinter.Button(root, text='+', command=increaseAlarmHours)
buttonIncreaseAlarmHours.pack()
buttonIncreaseAlarmHours.place(anchor="center", x=screenWidth/2-75, y=screenHeight-125, width=30, height=30)

buttonDecreaseAlarmHours=tkinter.Button(root, text="-", command=decreaseAlarmHours)
buttonDecreaseAlarmHours.pack()
buttonDecreaseAlarmHours.place(anchor="center", x=screenWidth/2-75, y=screenHeight-75, width=30, height=30)

labelAlarm=tkinter.Label(root, textvariable=alarmClockSelect, bg="black", fg="red", font=('arial', 30))
labelAlarm.pack()
labelAlarm.place(anchor="center", x=screenWidth/2, y=screenHeight-100)

buttonIncreaseAlarmMinutes=tkinter.Button(root, text='+', command=increaseAlarmMinutes)
buttonIncreaseAlarmMinutes.pack()
buttonIncreaseAlarmMinutes.place(anchor="center", x=screenWidth/2+75, y=screenHeight-125, width=30, height=30)

buttonDecreaseAlarmMinutes=tkinter.Button(root, text="-", command=decreaseAlarmMinutes)
buttonDecreaseAlarmMinutes.pack()
buttonDecreaseAlarmMinutes.place(anchor="center", x=screenWidth/2+75, y=screenHeight-75, width=30, height=30)

buttonExit=tkinter.Button(root, text="Exit", command=exit)
buttonExit.pack()
buttonExit.place(anchor="center", x=screenWidth-100, y=screenHeight-50, width=100, height=30)

root.mainloop()