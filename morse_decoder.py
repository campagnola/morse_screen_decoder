# import pyautogui as pag
import time
import scipy.stats
import pyqtgraph as pg
import numpy as np
from mss import mss

app = pg.mkQApp()

sct = mss()
signal = []

def get_ss():
    global roi
    # too slow
    # ss = np.array(pag.screenshot(region=[x[0], y[0], x[1]-x[0], y[1]-y[0]]))
    x, y = roi.pos()
    w, h = roi.size()
    ss = sct.grab(dict(top=int(y), left=int(x), height=int(h), width=int(w)))
    return np.array(ss)


def quantize_signal(sig):
    sig = np.array(sig)
    high = scipy.stats.scoreatpercentile(signal, 75)
    low = scipy.stats.scoreatpercentile(signal, 25)
    binary = np.round((sig - low) / (high - low)).astype(bool)
    return binary


def analyze_signal(sig):
    changes = np.argwhere(sig[1:] != sig[:-1])[:, 0]
    if sig[0]:
        changes = changes[1:]
    
    intervals = np.diff(changes)
    short = scipy.stats.mode(intervals).mode.mean()
    lengths = np.round(intervals / short)
    return lengths

def decode_signal(durations):
    decoded = ""
    pips = []
    i = 0
    while i < len(durations) - 2:
        on = durations[i]
        off = durations[i+1]
        i += 2
        pips.append(on > 2)
        if off > 2:
            decoded = decoded + get_letter(pips)
            pips = []
            if off > 6:
                decoded = decoded + " "
    return decoded


morse = {
    '.-': 'a',
    '-...': 'b',
    '-.-.': 'c',
    '-..': 'd',
    '.': 'e',
    '..-.': 'f',
    '--.': 'g',
    '....': 'h',
    '..': 'i',
    '.---': 'j',
    '-.-': 'k',
    '.-..': 'l',
    '--': 'm',
    '-.': 'n',
    '---': 'o',
    '.--.': 'p',
    '--.-': 'q',
    '.-.': 'r',
    '...': 's',
    '-': 't',
    '..-': 'u',
    '...-': 'v',
    '.--': 'w',
    '-..-': 'x',
    '-.--': 'y',
    '--..': 'z',
    '.-.-.-': '.',
    '--..--': ',',
    '..--..': '?',
    '-..-.': '/',
    '.--.-.': '@',
    '.----': '1',
    '..---': '2',
    '...--': '3',
    '....-': '4',
    '.....': '5',
    '-....': '6',
    '--...': '7',
    '---..': '8',
    '----.': '9',
    '-----': '0',
}


def get_letter(pips):
    pips = ''.join([('-' if x else '.') for x in pips])
    return morse.get(pips, '?')


def update_screenshot():
    ss = np.array(sct.grab({'top': 0, 'left': 0, 'width': 1000, 'height': 1000}))[..., :3]
    img.setImage(ss.transpose(1, 0, 2), autoLevels=False)

def reset_signal():
    global signal
    signal = []


win = pg.GraphicsLayoutWidget()
win.show()
win.resize(500, 800)

view = win.addViewBox(0, 0)
img = pg.ImageItem()
img.setLevels([0, 255])
view.addItem(img)
view.setAspectLocked()
view.setRange(xRange=[0, 1000], yRange=[0, 1000])
view.invertY()

roi = pg.RectROI([0, 0], [20, 20], pen='r')
roi.sigRegionChangeFinished.connect(reset_signal)
view.addItem(roi)

plt = win.addPlot(1, 0)
plt.setMaximumHeight(200)


last_ss = pg.ptime.time()

def update():
    global last_ss, signal, plt, imv, app
    now = pg.ptime.time()
    sleep = 0.02 - (now - last_ss)
    if sleep > 0:
        time.sleep(sleep)
    last_ss = now
    ss = get_ss()
    signal.append(-ss.mean())

    if len(signal) % 100 == 0:
        #imv.setImage(ss)
        update_screenshot()
        sig = quantize_signal(signal)
        plt.plot(sig.astype(int), clear=True)
        message = decode_signal(analyze_signal(sig))
        plt.setTitle(message[-100:])

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)


import sys
if sys.flags.interactive == 0:
    app.exec_()