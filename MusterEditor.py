import sys
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import *
from io import BytesIO
import time
from base64 import b64encode
import logging

from PIL import Image

from lib.MusterClass import TlbRec
from lib.MusterClass import PalRec
from lib.musterModule import bytes2int


# Tastatur Abfrage
def tasten(taste):  # Tastaturbehandlung für das Programm
    global pos_tlb_x_merken, pos_tlb_y_merken, kopieren, tlb_size
    # print(bin(taste.state))
    # print(taste)

    if (taste.state & 0x20000) == 0x20000:
        if taste.state & 0b1100 == 0b1100:  # Rechte Alt gedrückt wegen AND verknüpfung erst AltGR prüfen
            # Rechte Alt Taste gedrückt
            pass
            # if taste.keysym == "q":
            # programmBeenden()
        # Sondertaste gedrückt Alt
        elif taste.state & 0b1000 == 0b1000:  # Linke Alt gedrückt
            # Linke Alt Taste gedrückt
            if taste.keysym == "q":
                programmBeenden()
    elif (taste.state & 0x0004) == 0x4:  # CTRL gedrückt
        if taste.keysym == 'W':
            tlbScrollenHoch(10)
        if taste.keysym == 'A':
            tlbScrollenLinks(10)
        if taste.keysym == 'S':
            tlbScrollenRunter(10)
        if taste.keysym == 'D':
            tlbScrollenRechts(10)
        if taste.keysym == 'w':
            tlbScrollenHoch(1)
        if taste.keysym == 'a':
            tlbScrollenLinks(1)
        if taste.keysym == 's':
            tlbScrollenRunter(1)
        if taste.keysym == 'd':
            tlbScrollenRechts(1)
        if taste.keysym == 'Up':
            box_bewegen(0, tlb_size * -1)
        if taste.keysym == 'Down':
            box_bewegen(0, tlb_size)
        if taste.keysym == 'Left':
            box_bewegen(tlb_size * -1, 0)
        if taste.keysym == 'Right':
            box_bewegen(tlb_size, 0)
        if taste.keysym == 'c':
            kopieren = True
            pos_tlb_x_merken = pos_tlb_x
            pos_tlb_y_merken = pos_tlb_y
        if taste.keysym == 'v':
            tlbKopierenAnAktuellePosition()
    elif (taste.state & 0b1001) == 0b1001:  # Shift Taste gedrückt
        if taste.keysym == 'plus':  # +
            musterYPlus1()
        if taste.keysym == 'minus':  # -
            musterYMinus1()
        if taste.keysym == 'slash':  # /
            musterXMinus1()
        if taste.keysym == 'asterisk':  # *
            musterXPlus1()
        if taste.keysym == 'Up':
            box_bewegen(0, (tlb_size//2)*-1)
        if taste.keysym == 'Down':
            box_bewegen(0, (tlb_size//2))
        if taste.keysym == 'Left':
            box_bewegen((tlb_size//2)*-1, 0)
        if taste.keysym == 'Right':
            box_bewegen((tlb_size//2), 0)
        if taste.keysym == 'W':
            musterScrollenHoch(10)
        if taste.keysym == 'S':
            musterScrollenRunter(10)
        if taste.keysym == 'A':
            musterScrollenLinks(10)
        if taste.keysym == 'D':
            musterScrollenRechts(10)
    else:  # Normaler Tastendruck
        if taste.keysym == 'm':
            musterDraw()
        if taste.keysym == 'w':
            musterScrollenHoch(1)
        if taste.keysym == 's':
            musterScrollenRunter(1)
        if taste.keysym == 'a':
            musterScrollenLinks(1)
        if taste.keysym == 'd':
            musterScrollenRechts(1)
        if taste.keysym == 'plus':
            boxSetPlus1()
        if taste.keysym == 'minus':
            boxSetMinus1()
        if taste.keysym == 'Up':
            box_bewegen(0, - 1)
        if taste.keysym == 'Down':
            box_bewegen(0, + 1)
        if taste.keysym == 'Left':
            box_bewegen(-1, 0)
        if taste.keysym == 'Right':
            box_bewegen(+1, 0)
    return


# Box Aktionen
def boxSetPlus1():  # Boxgröße plus 1
    global tlb_size, pos_tlb_y, pos_tlb_x
    tlb_size += 1
    if tlb_size > box_max:
        tlb_size = box_max  # Verhindern das der tlb groesser wird als eine der Achsen
    if tlb_size > mus_gy or tlb_size > mus_gx:
        writeToLog('Box kann nicht groesser werden als kleinste Achse!')
        if mus_gy > mus_gx:
            tlb_size = mus_gx
        else:
            tlb_size = mus_gy
    # begrenzen des Wachstums der Scrollbar auf kleinste Achse - tlb mindestgröße
    if pos_tlb_x + tlb_size > mus_gx:
        pos_tlb_x -= 1
    if pos_tlb_y + tlb_size > mus_gy:
        pos_tlb_y -= 1
    set_sb_tlb()
    schreibeBoxInfos()
    setBox()
    tlbDraw()
    return


def boxSetMinus1():  # Boxgrösse minus 1
    global tlb_size, in_tlb_x, in_tlb_y, sb_y_tlb_maximum, sb_x_tlb_maximum
    tlb_size -= 1
    if tlb_size < box_min - 1:
        tlb_size = box_min - 1
    if in_tlb_x != 0:
        in_tlb_x -= 1
    if in_tlb_y != 0:
        in_tlb_y -= 1
    if sb_x_tlb_maximum != 0:
        sb_x_tlb_maximum -= 1
    if sb_y_tlb_maximum != 0:
        sb_y_tlb_maximum -= 1
    set_sb_tlb()
    schreibeBoxInfos()
    setBox()
    tlbDraw()
    return


def box_bewegen(x, y):  # Box an neue Position setzen
    global pos_tlb_x, pos_tlb_y
    pos_tlb_x += x
    pos_tlb_y += y
    if pos_tlb_x < 0:
        pos_tlb_x = 0
    if pos_tlb_y < 0:
        pos_tlb_y = 0
    if pos_tlb_x > mus_gx - tlb_size:
        pos_tlb_x = mus_gx - tlb_size
    if pos_tlb_y > mus_gy - tlb_size:
        pos_tlb_y = mus_gy - tlb_size
    tlbDraw()
    setBox()
    return


# Muster Größen Änderungen
def musterXPlus1():  # Mustergröße plus eins in X
    global mus_gx
    if mus_gx < mus_gx_max - 1:
        mus_gx += 1
        schreibeBoxInfos()
    return


def musterYPlus1():  # Mustergröße plus eins in Y
    global mus_gy
    if mus_gy < mus_gy_max + 1:
        mus_gy += 1
        schreibeBoxInfos()
    return


def musterXMinus1():  # Mustergröße minus eins in X
    global mus_gx
    if mus_gx > tlb_size:
        mus_gx -= 1
        schreibeBoxInfos()
    return


def musterYMinus1():  # Mustergröße minus eins in Y
    global mus_gy
    if mus_gy > tlb_size:
        mus_gy -= 1
        schreibeBoxInfos()
    return


def set_sb_tlb():  # Scrollbar's im Teilbereich nach Änderung Boxgrüße anpassen
    global sb_x_tlb_maximum, sb_y_tlb_maximum
    sb_x_tlb_maximum = tlb_size - tlb_anzahl_felder + 1
    sb_y_tlb_maximum = tlb_size - tlb_anzahl_felder + 1
    regler_laenge = (tlb_anzahl_felder - sb_x_tlb_maximum) * tlb_feld_size
    if tlb_size + 1 < tlb_anzahl_felder:
        regler_laenge = tlb_feld_size * tlb_anzahl_felder
    if regler_laenge < 20:
        regler_laenge = 20
    tlbReglerX['to'] = sb_x_tlb_maximum
    tlbReglerX['sliderlength'] = regler_laenge
    tlbReglerY["to"] = sb_y_tlb_maximum
    tlbReglerY['sliderlength'] = regler_laenge
    return


def schreibeBoxInfos():  # Infos zur Box über Muster aktualisieren
    frameMuster['text'] = "Box Size = " + str(tlb_size+1) + "; Gx : " + str(mus_gx+1) + "; Gy : " + str(mus_gy+1) +\
                          "; Box Pos x=" + str(pos_tlb_x+1) + " y="+str(pos_tlb_y+1)
    return


def palReDraw():  # Malt die Ganze Farbpalette neu (z.B. nach Laden einer neuen Palette)
    k = 0
    for i in pal:
        i.setColorRGB(vga_pal_rot[k], vga_pal_gruen[k], vga_pal_blau[k])
        k += 1
        i.drawME()
    return


def tlbDraw():  # Malt den Teilbereich neu (nach Tlb oder Muster Aktionen wie Spiegeln etc.)
    starteZeitmessung()
    for i in range(0, tlb_anzahl_felder):
        for t in range(0, tlb_anzahl_felder):
            k = muster_feld[pos_tlb_x + in_tlb_x + i][pos_tlb_y + in_tlb_y + t]
            tlb[i + t * tlb_anzahl_felder].setColorRGB(vga_pal_rot[k], vga_pal_gruen[k], vga_pal_blau[k])
            tlb[i + t * tlb_anzahl_felder].drawME()
    stopZeitmessung('Teilbereich neu Zeichnen alles')
    return


def tlbAktReDraw(refarbe=-1):  # Malt die übergebene Farbe im Teilbereich neu
    if refarbe == -1:
        refarbe = akt_farbe  # keine Farbe übergeben dann nehme aktuelle Farbe
    starteZeitmessung()
    for i in range(0, tlb_anzahl_felder):
        for t in range(0, tlb_anzahl_felder):
            k = muster_feld[pos_tlb_x + in_tlb_x + i][pos_tlb_y + in_tlb_y + t]
            if k == refarbe:
                tlb[i + t * tlb_anzahl_felder].setColorRGB(vga_pal_rot[k], vga_pal_gruen[k], vga_pal_blau[k])
                tlb[i + t * tlb_anzahl_felder].drawME()
    stopZeitmessung('Teilbereich neu Zeichnen aktuelle Farbe')
    return


def musterDraw():  # Malt das ganze Muster neu (nach Muster Aktionen spiegeln etc.)
    starteZeitmessung()
    global musterImg
    for ii in range(0, mus_gx + 1):
        for tt in range(0, mus_gy + 1):
            palette = muster_feld[ii][tt]
            nfarbe = "#" + format(vga_pal_rot[palette], '02x') + format(vga_pal_gruen[palette], '02x') +\
                     format(vga_pal_blau[palette], '02x')
            musterImg.put(nfarbe, (ii, tt))
    stopZeitmessung('Musterdraw ' + str(mus_gx) + '*' + str(mus_gy))
    return


def musterDrawTlb():  # Malt den Teilbereich im Muster neu (nach TLB Aktionen drehen etc.)
    starteZeitmessung()
    global musterImg
    for ii in range(pos_tlb_x, pos_tlb_x + tlb_size+1):
        for tt in range(pos_tlb_y, pos_tlb_y + tlb_size+1):
            palette = muster_feld[ii][tt]
            nfarbe = "#" + format(vga_pal_rot[palette], '02x') + format(vga_pal_gruen[palette], '02x') +\
                     format(vga_pal_blau[palette], '02x')
            musterImg.put(nfarbe, (ii, tt))
    stopZeitmessung('Musterdraw Teilbereich alles ' + str(tlb_size) + '*' + str(tlb_size))
    return


def musterAktReDraw(farbwert=-1):  # Malt die übergebene Farbe im Muster neu
    starteZeitmessung()
    global musterImg
    if farbwert == -1:
        farbwert = akt_farbe
    for ii in range(0, mus_gx + 1):
        for tt in range(0, mus_gy + 1):
            palette = muster_feld[ii][tt]
            if palette == farbwert:
                nfarbe = "#" + format(vga_pal_rot[palette], '02x') + format(vga_pal_gruen[palette], '02x') +\
                         format(vga_pal_blau[palette], '02x')
                musterImg.put(nfarbe, (ii, tt))
    stopZeitmessung('Musterdraw Aktuelle Farbe ' + str(mus_gx) + '*' + str(mus_gy))
    return


def tlbCanvasMouseMove(event):  # Event Mausbewegung im Teilbereich, malt bei gedrückt gehaltener Maustaste ins Tlb Feld
    button = 0
    global button1pressed
    global button2pressed
    global button3pressed
    global akt_farbe, hin_farbe
    # print(event)
    if event.num == 1 or button1pressed:  # "Linke Maustaste" Feld mit aktueller Farbe füllen
        button = "1"
        button1pressed = True
        tlbFeldFuellen(event.x, event.y, akt_farbe)
    if event.num == 2:  # "Mittlere Maustaste" pickt Farbe unter dem Cursor auf und setzt sie als Aktuelle Farbe
        button = "2"
        neue_farbe = muster_feld[pos_tlb_x + (int(event.x / tlb_feld_size))][pos_tlb_y + (int(event.y / tlb_feld_size))]
        if neue_farbe == hin_farbe:
            hin_farbe = neue_farbe
            palFarbeTauschen()
        if neue_farbe != hin_farbe:
            pal[akt_farbe].unselect()
            pal[akt_farbe].drawME()
            pal[neue_farbe].select()
            pal[neue_farbe].xcross(True)
            pal[neue_farbe].drawME()
            akt_farbe = neue_farbe
            palAktFarbeReDraw()
    if event.num == 3 or button3pressed:  # "Rechte Maustaste" Feld mit Hintergrundfarbe füllen
        button = "3"
        tlbFeldFuellen(event.x, event.y, hin_farbe)
    statusleiste["text"] = "TLBCanvas MouseX: " + str(event.x) + " MouseY: " + str(event.y) + " Button: " + str(button)
    return


def tlbCanvasMouseDown(event):  # Event Mausklick im Teilbereich verarbeiten
    global button1pressed
    global button2pressed
    global button3pressed
    global akt_farbe, hin_farbe
    button = 0
    # print(event)
    if event.num == 1:  # Linke Maustaste
        button = "1"
        button1pressed = True
        tlbFeldFuellen(event.x, event.y, akt_farbe)
    if event.num == 2:  # Mittlere Maustaste
        button = "2"
        neue_farbe = muster_feld[pos_tlb_x + (int(event.x / tlb_feld_size))][pos_tlb_y + (int(event.y / tlb_feld_size))]
        if neue_farbe == hin_farbe:
            hin_farbe = neue_farbe
            palFarbeTauschen()
        if neue_farbe != hin_farbe:
            pal[akt_farbe].unselect()
            pal[akt_farbe].drawME()
            pal[neue_farbe].select()
            pal[neue_farbe].xcross(True)
            pal[neue_farbe].drawME()
            akt_farbe = neue_farbe
            palAktFarbeReDraw()
    if event.num == 3:  # Rechte Maustaste
        button = "3"
        button3pressed = True
        tlbFeldFuellen(event.x, event.y, hin_farbe)
    statusleiste["text"] = "TLBCanvas MouseX: " + str(event.x) + " MouseY: " + str(event.y) + " Button: " + str(button)
    return


def tlbCanvasMouseUp(_event=None):  # Event Maustaste losgelassen im Teilbereich verarbeiten
    global button1pressed
    global button2pressed
    global button3pressed
    button1pressed = False
    button2pressed = False
    button3pressed = False
    return


def setBox():  # Positioniert die Box neu im Mustercanvas
    musterCanvas.coords(dragBox, pos_bm_x + pos_tlb_x - 4, pos_bm_y + pos_tlb_y - 4,
                        pos_bm_x + pos_tlb_x - 1 + tlb_size + 4, pos_bm_y + pos_tlb_y - 1 + tlb_size + 4)
    schreibeBoxInfos()
    lupeDraw()
    return


def musterCanvasMouseMove(event):  # Maus auf Canvas Bewegt; dient zum Draggen der Box
    button = 0
    global button1pressed
    global button3pressed
    global drag_the_box, pos_tlb_x, pos_tlb_y
    if event.num == 1 or button1pressed:  # Linke Maustaste
        button = "1"
        button1pressed = True
        if drag_the_box:
            # boxaus()
            pos_tlb_x = int((event.x - pos_bm_x) - tlb_size / 2)
            pos_tlb_y = int((event.y - pos_bm_y) - tlb_size / 2)
            if pos_tlb_x < 0:
                pos_tlb_x = 0
            if pos_tlb_y < 0:
                pos_tlb_y = 0
            if pos_tlb_x > mus_gx - tlb_size:
                pos_tlb_x = mus_gx - tlb_size
            if pos_tlb_y > mus_gy - tlb_size:
                pos_tlb_y = mus_gy - tlb_size
            setBox()
            tlbDraw()
    if event.num == 2:  # "Mittlere Maustaste
        button = "2"
        pass
    if event.num == 3 or button3pressed:  # Rechte Maustaste
        button = "3"
    statusleiste["text"] = "MusterCanvas MouseX: " + str(event.x) + " MouseY: " + str(event.y) +\
                           " Button: " + str(button) + " posTLBX: " + str(pos_tlb_x) + " posTLBY: " + str(pos_tlb_y)
    return


def musterCanvasMouseDown(event):  # Event Maus im Musterbereich Taste gedrückt verarbeiten
    global button1pressed
    global button3pressed
    global drag_the_box, pos_tlb_x, pos_tlb_y
    button = 0
    global akt_farbe
    # print(event)
    x = event.x
    y = event.y
    if event.num == 1:  # Linke Maustaste
        button = "1"
        if (x >= pos_tlb_x + pos_bm_x) and (x <= pos_tlb_x + pos_bm_x + tlb_size) and (y >= pos_tlb_y + pos_bm_y) and (
                y <= pos_tlb_y + pos_bm_y + tlb_size):
            drag_the_box = True
            button1pressed = True
    if event.num == 2:  # Mittlere Maustaste
        button = "2"
    if event.num == 3:  # Rechte Maustaste
        button = "3"
        button3pressed = True
        pos_tlb_x = int((event.x - pos_bm_x) - tlb_size / 2)
        pos_tlb_y = int((event.y - pos_bm_y) - tlb_size / 2)
        if pos_tlb_x < 0:
            pos_tlb_x = 0
        if pos_tlb_y < 0:
            pos_tlb_y = 0
        if pos_tlb_x > mus_gx - tlb_size:
            pos_tlb_x = mus_gx - tlb_size
        if pos_tlb_y > mus_gy - tlb_size:
            pos_tlb_y = mus_gy - tlb_size
        tlbDraw()
        setBox()
    statusleiste["text"] = "TLBCanvas MouseX: " + str(event.x) + " MouseY: " + str(event.y) + " Button: " + str(button)
    return


def musterCanvasMouseUp(_event=None):  # Event Maus im Musterbereich Taste losgelassen verarbeiten
    global button1pressed
    global button3pressed
    global drag_the_box
    button1pressed = False
    button3pressed = False
    drag_the_box = False
    return


def tlbKopierenAnAktuellePosition():  # Kopiert den mit 'ctrl-c' ausgewählten Teilbereich an aktuelle Boxposition
    global muster_feld
    if kopieren:
        puffer = [[0 for _ in range(tlb_size + 1)] for _ in range(tlb_size + 1)]
        for i in range(0, tlb_size + 1):
            for t in range(0, tlb_size + 1):
                puffer[t][i] = muster_feld[pos_tlb_x_merken + t][pos_tlb_y_merken + i]
        for i in range(0, tlb_size + 1):
            for t in range(0, tlb_size + 1):
                muster_feld[pos_tlb_x + t][pos_tlb_y + i] = puffer[t][i]
    musterDrawTlb()
    tlbDraw()
    return


def tlbFeldFuellen(x, y, color):  # Angeklicktes Feld im Teilbereich füllen und neu Zeichnen
    global musterImg
    global muster_feld
    if tlb_feld_size * tlb_anzahl_felder >= x >= 0 and tlb_feld_size * tlb_anzahl_felder >= y >= 0:
        x = int(x // tlb_feld_size)
        if x >= tlb_anzahl_felder:
            x = tlb_anzahl_felder - 1
        if x > tlb_size:  # Abbruch wenn Malbereich ausserhalb der Box
            writeToLog('Mal Aktion ausserhalb der Box! Nicht gestattet.')
            return
        y = int(y // tlb_feld_size)
        if y >= tlb_anzahl_felder:
            y = tlb_anzahl_felder - 1
        if y > tlb_size:  # Abbruch wenn Malbereich ausserhalb der Box
            writeToLog('Mal Aktion ausserhalb der Box! Nicht gestattet.')
            return
        z = x + (y * tlb_anzahl_felder)
        if z > tlb_anzahl_felder * tlb_anzahl_felder:
            z = tlb_anzahl_felder * tlb_anzahl_felder
        tlb[z].setColorRGB(vga_pal_rot[color], vga_pal_gruen[color], vga_pal_blau[color])
        tlb[z].drawME()
        muster_feld[pos_tlb_x + in_tlb_x + x][pos_tlb_y + in_tlb_y + y] = color
        nfarbe = "#" + format(vga_pal_rot[color], '02x') + format(vga_pal_gruen[color], '02x') + \
                 format(vga_pal_blau[color], '02x')
        musterImg.put(nfarbe, (pos_tlb_x + in_tlb_x + x, pos_tlb_y + in_tlb_y + y))
    return


def palCanvasMouse(event):  # Event Behandlung Maus Aktion in Palette
    button = 0
    global hin_farbe, redrawR, redrawG, redrawB
    global akt_farbe
    if farb_feld_size * 16 >= event.x >= 0 and farb_feld_size * 16 >= event.y >= 0:
        x = int(event.x / farb_feld_size)
        y = int(event.y / farb_feld_size)
        z = x + (y * 16)
    # print(event)
        redrawR = False
        redrawG = False
        redrawB = False
        if event.num == 1:  # Linke Maustaste
            button = "1"
            if z == hin_farbe:  # Tausche Vordergrund und Hintergrund Farbe
                palFarbeTauschen()
            else:
                pal[akt_farbe].unselect()
                pal[akt_farbe].drawME()
                akt_farbe = z
                pal[z].select()
                pal[z].xcross(True)
                pal[z].drawME()
                palAktFarbeReDraw()
        if event.num == 2:  # Mittlere Maustaste
            button = "2"

        if event.num == 3:  # Rechte Maustaste
            button = "3"
            if z == akt_farbe:  # Tausche Vorder und Hintergrund Farbe
                palFarbeTauschen()
            else:
                pal[hin_farbe].unselect()
                pal[hin_farbe].drawME()
                hin_farbe = z
                pal[z].select()
                pal[z].xcross(False)
                pal[z].drawME()
                palHinFarbeReDraw()
    statusleiste["text"] = "PALCanvas MouseX: " + str(event.x) + " MouseY: " + str(event.y) + " Button: " + str(button)
    return


# Funktionen zum Datei Menu
def musterNeu():  # Muster Editor auf Anfang
    global muster_feld, mus_gx, mus_gy, pos_tlb_x, pos_tlb_y
    for i in range(0, mus_gx_max + 1):
        for t in range(0, mus_gy_max + 1):
            muster_feld[i][t] = 0
    mus_gx = mus_gx_max
    mus_gy = mus_gy_max
    pos_tlb_x = 0
    pos_tlb_y = 0
    musterDraw()
    tlbDraw()
    setBox()
    return


def musterSpeichern():  # Auswahl Dateiname für Muster speichern
    file = filedialog.asksaveasfilename(initialdir="/", title="Palette Speichern", defaultextension=".muster",
                                        filetypes=(("muster files", "*.muster"), ("all files", "*.*")))
    # Savefiledialog
    if len(file) > 0:
        okay = musterSave(file)
        if okay:
            messagebox.showinfo('OK', 'Muster wurde gespeichert!')
        else:
            messagebox.showerror('Fehler', 'Muster konnte nicht gesichert werden!')
    return


def musterSave(dateiname):  # Muster speichern
    try:
        musterfile = open(dateiname, 'wb')
        # Muster speichern
        # Größe speichern
        musterfile.write(mus_gx.to_bytes(length=2, byteorder='little'))
        musterfile.write(mus_gy.to_bytes(length=2, byteorder='little'))
        # Palette speichern
        for t in range(0, 256):
            musterfile.write(vga_pal_rot[t].to_bytes(length=1, byteorder='big'))
            musterfile.write(vga_pal_gruen[t].to_bytes(length=1, byteorder='big'))
            musterfile.write(vga_pal_blau[t].to_bytes(length=1, byteorder='big'))
        for i in range(0, mus_gy + 1):
            for t in range(0, mus_gx + 1):
                musterfile.write(muster_feld[t][i].to_bytes(length=1, byteorder='big'))
        musterfile.close()
        logging.info('Muster ' + dateiname + ' wurde gespeichert.')
        return True
    except IOError:
        logging.error('*musterSave* Muster konnte nicht gespeichert werden ' + dateiname)
        return False


def pngAlphaLaden():  # Auswahl Dateinamen PNG Alpha Kanal als Muster zum laden
    global tlb_size
    # Openfiledialog
    file = filedialog.askopenfilename(initialdir="/", title="PNG Oeffnen",
                                      filetypes=(("portable network grafiks", "*.png"), ("all files", "*.*")))
    if len(file) > 0:
        okay = pngAlphaLoad(file)
        if okay:
            musterDraw()
            resetBox()
            tlbDraw()
            palReDraw()
            messagebox.showinfo('OK', 'PNG wurde geladen!')
        else:
            messagebox.showerror('Fehler', 'PNG konnte nicht geladen werden!')
    return


def pngAlphaLoad(dateiname):  # PNG als Muster Laden Alpha Kanal als Grauwerte
    global mus_gx, mus_gy, pos_tlb_y, pos_tlb_x
    global vga_pal_gruen, vga_pal_blau, vga_pal_rot
    try:
        bild = Image.open(dateiname)
        # Bildmode Prüfen RGBA RGB P ? 32 Bit Shadow Bilder
        (breite, hoehe) = bild.size
        if breite > mus_gx_max or hoehe > mus_gy_max:
            messagebox.showerror('Fehler', 'PNG ueberschreitet die zulaessige Groesse von ' + str(mus_gx_max)
                                 + ' x ' + str(
                mus_gy_max))
            return False
        else:
            if bild.mode == 'RGBA':
                # Analyse Farbpalette max 256 Farben
                pal_r = [x for x in range(0, 256)]
                pal_g = [x for x in range(0, 256)]
                pal_b = [x for x in range(0, 256)]

                schonda = False
                # erste Farbe festlegen Graustufen für Alpha Blending
                dummy = bild.getpixel((0, 0))
                pal_r[0] = dummy[3]
                pal_g[0] = dummy[3]
                pal_b[0] = dummy[3]
                z = 1  # Paletten position zum fortfahren
                for x in range(0, breite):
                    for y in range(0, hoehe):
                        dummy = bild.getpixel((x, y))
                        for i in range(0, z-1):
                            if pal_r[i] == dummy[3] and pal_g[i] == dummy[3] and pal_b[i] == dummy[3]:
                                schonda = True
                        if not schonda:  # Farbe zur Palette hinzu
                            pal_r[z] = dummy[3]
                            pal_g[z] = dummy[3]
                            pal_b[z] = dummy[3]
                            z += 1
                            if z >= 256:
                                messagebox.showerror('Fehler', 'PNG hat mehr als 256 Farben und ist nicht Darstellbar!')
                                return
                        schonda = False
                for x in range(0, breite):
                    for y in range(0, hoehe):
                        dummy = bild.getpixel((x, y))  # Laden der Pixel ins MusterFeld
                        for i in range(0, z + 1):  # nur bis zur ermittelten Anzahl Farben
                            if pal_r[i] == dummy[3] and pal_g[i] == dummy[3] and pal_b[i] == dummy[3]:
                                muster_feld[x][y] = i
                                break

                # Übertrage die Farben in die eigentliche Palette mit Anpassung auf Graustufen
                for t in range(0, z + 1):
                    vga_pal_rot[t] = 255 - pal_r[t]
                    vga_pal_gruen[t] = 255 - pal_g[t]
                    vga_pal_blau[t] = 255 - pal_b[t]
            else:
                messagebox.showerror('Fehler', 'PNG besitzt keinen Alpha Kanal')
                return False
            # Setzen des Musters auf Größe des Bildes
            mus_gx = breite - 1
            mus_gy = hoehe - 1
            logging.info("PNG analysiert " + dateiname + " in Muster uebertragen")
            bild.close()
        return True

    except IOError:
        logging.error("*pngLoad* Bild Laden fehlgeschlagen" + dateiname)
        return False


def pngLaden():  # Auswahl Dateinamen Muster zum laden
    global tlb_size
    # Openfiledialog
    file = filedialog.askopenfilename(initialdir="/", title="PNG Oeffnen",
                                      filetypes=(("portable network grafiks", "*.png"), ("all files", "*.*")))
    if len(file) > 0:
        okay = pngLoad(file)
        if okay:
            musterDraw()
            resetBox()
            tlbDraw()
            palReDraw()
            messagebox.showinfo('OK', 'PNG wurde geladen!')
        else:
            messagebox.showerror('Fehler', 'PNG konnte nicht geladen werden!')
    return


def pngLoad(dateiname):  # PNG als Muster Laden
    global mus_gx, mus_gy, pos_tlb_y, pos_tlb_x
    global vga_pal_gruen, vga_pal_blau, vga_pal_rot
    try:
        bild = Image.open(dateiname)
        (breite, hoehe) = bild.size
        # Abfangen wenn das PNG die maximal Größe überschreitet
        if breite > mus_gx_max or hoehe > mus_gy_max:
            messagebox.showerror('Fehler', 'PNG ueberschreitet die zulaessige Groesse von ' + str(mus_gx_max)
                                 + ' x ' + str(
                mus_gy_max))
            return False  # Bild kann nicht geladen werden, zurück
        else:
            if bild.mode == 'RGBA' or bild.mode == 'RGB':  # Prüfe ob ein Truecolor Bild vorliegt
                # Analyse Farbpalette max 256 Farben
                pal_r = [x for x in range(0, 256)]  # Farbfelder für Farbanalyse bereitstellen
                pal_g = [x for x in range(0, 256)]
                pal_b = [x for x in range(0, 256)]
                schonda = False  # True wenn die Farbe bereits erkannt wurde
                # erste Farbe festlegen
                dummy = bild.getpixel((0, 0))
                pal_r[0] = dummy[0]
                pal_g[0] = dummy[1]
                pal_b[0] = dummy[2]
                z = 1  # Paletten position zum fortfahren
                for x in range(0, breite):  # Untersuch das ganze Bild nach Farben und halte diese in der Palette fest
                    for y in range(0, hoehe):
                        dummy = bild.getpixel((x, y))
                        for i in range(0, z-1):  # Prüfung ob Farbe schon gefunden wurde
                            if pal_r[i] == dummy[0] and pal_g[i] == dummy[1] and pal_b[i] == dummy[2]:
                                schonda = True  # Farbe schon in Palette
                        if not schonda:  # Farbe zur Palette hinzu
                            pal_r[z] = dummy[0]
                            pal_g[z] = dummy[1]
                            pal_b[z] = dummy[2]
                            z += 1
                            if z >= 256:  # wenn gefundene Farben den Maximalwert überschreiten dann Abbruch
                                messagebox.showerror('Fehler', 'PNG hat mehr als 256 Farben und ist nicht Darstellbar!')
                                return
                        schonda = False
                # Übertrage die Farben in die eigentliche Palette
                for t in range(0, z + 1):
                    vga_pal_rot[t] = pal_r[t]
                    vga_pal_gruen[t] = pal_g[t]
                    vga_pal_blau[t] = pal_b[t]
                # Analysiere die Farben jedes Pixels und stelle den Farbwert in das Muster
                for x in range(0, breite):
                    for y in range(0, hoehe):
                        dummy = bild.getpixel((x, y))  # Laden der Pixel ins MusterFeld
                        # nur bis zur ermittelten Anzahl Farben, vermeidet Fehler und spart Zeit
                        for i in range(0, z + 1):
                            if pal_r[i] == dummy[0] and pal_g[i] == dummy[1] and pal_b[i] == dummy[2]:
                                muster_feld[x][y] = i
                                break  # Farbe wurde gefunden Schleife beenden und mit nächstem Pixel fortfahren
            # Prüfung ob Bild im Modus P vorliegt, also mit Palette mit 256 Farben
            elif bild.mode == 'P':
                palette = bild.getpalette()
                t = 0
                for i in range(0, len(palette), 3):  # Palette ist konform zur internen Palette also einfach übertragen
                    vga_pal_rot[t] = palette[i]
                    vga_pal_gruen[t] = palette[i+1]
                    vga_pal_blau[t] = palette[i+2]
                    t += 1
                # Nun noch das Image in das Muster lesen, ebenfalls Gleichwertig mit internem Verfahren
                for x in range(0, breite):
                    for y in range(0, hoehe):
                        muster_feld[x][y] = bild.getpixel((x, y))  # Laden der Pixel ins MusterFeld
            # Prüfung ob Bild im 'L' Modus vorliegt entspricht Graustufen Bild
            elif bild.mode == 'L':
                for i in range(0, 256):  # Palette als Graustufen anlegen
                    vga_pal_rot[i] = i
                    vga_pal_gruen[i] = i
                    vga_pal_blau[i] = i
                for x in range(0, breite):  # Übertragen des Image in das Muster
                    for y in range(0, hoehe):
                        muster_feld[x][y] = bild.getpixel((x, y))  # Laden der Pixel ins MusterFeld
            mus_gx = breite - 1  # Anpassen des Musters an geladene Größe
            mus_gy = hoehe - 1
            logging.info("PNG analysiert " + dateiname + " in Muster uebertragen")
            bild.close()
        return True  # Alles erfolgreich

    except IOError:  # Fehler beim öffnen der Image Datei
        logging.error("*pngLoad* Bild Laden fehlgeschlagen" + dateiname)
        return False


def musterLaden():  # Auswahl Dateinamen Muster zum laden
    global tlb_size, sb_x_tlb_maximum, sb_y_tlb_maximum
    # Openfiledialog
    file = filedialog.askopenfilename(initialdir="/", title="Muster Oeffnen",
                                      filetypes=(("muster files", "*.muster"), ("all files", "*.*")))
    if len(file) > 0:
        okay = musterLoad(file)
        if okay:
            musterDraw()
            if mus_gy < tlb_size or mus_gx < tlb_size:
                tlb_size = min(mus_gx, mus_gy)
            # box und Scrollbars zurücksetzen
            resetBox()
            sb_x_tlb_maximum = 0
            sb_y_tlb_maximum = 0
            set_sb_tlb()
            tlbDraw()
            palReDraw()
            messagebox.showinfo('OK', 'Muster wurde geladen!')
        else:
            messagebox.showerror('Fehler', 'Muster konnte nicht geladen werden!')
    return


def musterLoad(dateiname):  # Muster Laden
    global mus_gx, mus_gy, pos_tlb_y, pos_tlb_x
    global vga_pal_gruen, vga_pal_blau, vga_pal_rot
    try:
        musfile = open(dateiname, 'rb')
        # Größe des Musters Laden
        mus_gx = bytes2int(musfile.read(2))
        mus_gy = bytes2int(musfile.read(2))
        # Palette laden
        for t in range(0, 256):
            vga_pal_rot[t] = bytes2int(musfile.read(1))
            vga_pal_gruen[t] = bytes2int(musfile.read(1))
            vga_pal_blau[t] = bytes2int(musfile.read(1))
        # Muster Laden
        for i in range(0, mus_gy + 1):
            for t in range(0, mus_gx + 1):
                muster_feld[t][i] = bytes2int(musfile.read(1))
        pos_tlb_x = 0
        pos_tlb_y = 0
        musfile.close()
        logging.info("Muster " + dateiname + " erfolgreich geladen")
        return True
    except IOError:
        logging.error("*musterLoad* Muster Laden fehlgeschlagen" + dateiname)
        return False


def musterAltLaden():  # Auswahl Dateinamen Muster laden altes Format
    global tlb_size, sb_x_tlb_maximum, sb_y_tlb_maximum
    file = filedialog.askopenfilename(initialdir="/", title="Muster Oeffnen",
                                      filetypes=(("muster files", "*.mus"), ("all files", "*.*")))
    # Openfiledialog

    if len(file) > 0:
        okay = musterLoadOld(file)
        if okay:
            musterDraw()
            if mus_gy < tlb_size or mus_gx < tlb_size:
                tlb_size = min(mus_gy, mus_gx)
            # box und Scrollbars zurücksetzen
            resetBox()
            sb_x_tlb_maximum = 0
            sb_y_tlb_maximum = 0
            set_sb_tlb()
            tlbDraw()
            palReDraw()
            messagebox.showinfo('OK', 'Muster wurde geladen!')
        else:
            messagebox.showerror('Fehler', 'Muster konnte nicht geladen werden!')
    return


def musterLoadOld(dateiname):  # Muster laden altes Dateiformat
    global mus_gx, mus_gy, pos_tlb_y, pos_tlb_x
    global vga_pal_gruen, vga_pal_blau, vga_pal_rot
    try:
        musfile = open(dateiname, 'rb')
        # Größe des Musters Laden
        mus_gx = bytes2int(musfile.read(2))
        mus_gy = bytes2int(musfile.read(2))
        # Muster Laden
        for i in range(0, mus_gy + 1):
            for t in range(0, mus_gx + 1):
                muster_feld[t][i] = bytes2int(musfile.read(1))
        # Palette laden
        for t in range(0, 256):
            vga_pal_rot[t] = bytes2int(musfile.read(1))
            vga_pal_gruen[t] = bytes2int(musfile.read(1))
            vga_pal_blau[t] = bytes2int(musfile.read(1))
        # Palette konvertieren
        for t in range(0, 256):
            # Rot ton hoch rechnen
            if 63 > vga_pal_rot[t] > 0:
                dumm = vga_pal_rot[t] * 4
                vga_pal_rot[t] = int(dumm)
            elif vga_pal_rot[t] == 63:
                vga_pal_rot[t] = 255
            # Grün ton
            if 63 > vga_pal_gruen[t] > 0:
                dumm = vga_pal_gruen[t] * 4
                vga_pal_gruen[t] = int(dumm)
            elif vga_pal_gruen[t] == 63:
                vga_pal_gruen[t] = 255
            # Blau ton
            if 63 > vga_pal_blau[t] > 0:
                dumm = vga_pal_blau[t] * 4
                vga_pal_blau[t] = int(dumm)
            elif vga_pal_blau[t] == 63:
                vga_pal_blau[t] = 255
        pos_tlb_x = 0
        pos_tlb_y = 0
        musfile.close()
        logging.info("Muster " + dateiname + "erfolgreich geladen")
        return True
    except IOError:
        logging.error("*musterLoadOld* Muster Laden fehlgeschlagen" + dateiname)
        return False


def palLadenAlt():  # Asuwahl Dateinamen alte Farbpalette zum laden
    file = filedialog.askopenfilename(initialdir="/", title="Palette Oeffnen",
                                      filetypes=(("palette files", "*.pal"), ("all files", "*.*")))
    # Openfiledialog
    if len(file) > 0:
        okay = palLoadAlt(file)
        if okay:
            musterDraw()
            tlbDraw()
            palReDraw()
            messagebox.showinfo('OK', 'Palette wurde geladen!')
        else:
            messagebox.showerror('Fehler', 'Palette konnte nicht geladen werden!')
    return


def palLoadAlt(dateiname):  # Alte Farbpalette laden und anpassen
    global vga_pal_gruen, vga_pal_blau, vga_pal_rot
    try:
        palette = open(dateiname, 'rb')
        # Palette laden
        for t in range(0, 256):
            vga_pal_rot[t] = bytes2int(palette.read(1))
            vga_pal_gruen[t] = bytes2int(palette.read(1))
            vga_pal_blau[t] = bytes2int(palette.read(1))
        # Palette konvertieren
        for t in range(0, 256):
            # Rot ton hoch rechnen
            if 63 > vga_pal_rot[t] > 0:
                dumm = vga_pal_rot[t] * 4
                vga_pal_rot[t] = int(dumm)
            elif vga_pal_rot[t] == 63:
                vga_pal_rot[t] = 255
            # Grün ton
            if 63 > vga_pal_gruen[t] > 0:
                dumm = vga_pal_gruen[t] * 4
                vga_pal_gruen[t] = int(dumm)
            elif vga_pal_gruen[t] == 63:
                vga_pal_gruen[t] = 255
            # Blau ton
            if 63 > vga_pal_blau[t] > 0:
                dumm = vga_pal_blau[t] * 4
                vga_pal_blau[t] = int(dumm)
            elif vga_pal_blau[t] == 63:
                vga_pal_blau[t] = 255
        palette.close()
        logging.info("Palette " + dateiname + "erfolgreich geladen")
        return True
    except IOError:
        logging.error("*palLoadAlt* Palette Laden fehlgeschlagen" + dateiname)
        return False


def palSpeichern():  # Auswahl Dateiname für Farbpalette speichern
    file = filedialog.asksaveasfilename(initialdir="/", title="Palette Speichern", defaultextension=".palette",
                                        filetypes=(("palette files", "*.palette"), ("all files", "*.*")))
    # Savefiledialog
    if len(file) > 0:
        okay = palSave(file)
        if okay:
            messagebox.showinfo('OK', 'Palette wurde gespeichert!')
        else:
            messagebox.showerror('Fehler', 'Palette konnte nicht gesichert werden!')
    return


def palSave(dateiname):  # Farbpalette speichern
    try:
        palette = open(dateiname, 'wb')
        # Palette speichern
        for t in range(0, 256):
            palette.write(vga_pal_rot[t].to_bytes(length=1, byteorder='big'))
            palette.write(vga_pal_gruen[t].to_bytes(length=1, byteorder='big'))
            palette.write(vga_pal_blau[t].to_bytes(length=1, byteorder='big'))
        palette.close()
        logging.info("Palette " + dateiname + "erfolgreich gespeichert")
        return True
    except IOError:
        logging.error("*palSave* Palette Speichern fehlgeschlagen" + dateiname)
        return False


def palLaden():  # Dateinamenauswahl für Farbpalette laden
    file = filedialog.askopenfilename(initialdir="/", title="Palette Oeffnen",
                                      filetypes=(("palette files", "*.palette"), ("all files", "*.*")))
    # Openfiledialog
    if len(file) > 0:
        okay = palLoad(file)
        if okay:
            musterDraw()
            tlbDraw()
            palReDraw()
            messagebox.showinfo('OK', 'Palette wurde geladen!')
        else:
            messagebox.showerror('Fehler', 'Palette konnte nicht geladen werden!')
    return


def palLoad(dateiname):  # Farbpalette laden
    global vga_pal_gruen, vga_pal_blau, vga_pal_rot
    try:
        palette = open(dateiname, 'rb')
        # Palette laden
        for t in range(0, 256):
            vga_pal_rot[t] = bytes2int(palette.read(1))
            vga_pal_gruen[t] = bytes2int(palette.read(1))
            vga_pal_blau[t] = bytes2int(palette.read(1))
        palette.close()
        logging.info('Palette ' + dateiname + ' wurde geladen.')
        return True
    except IOError:
        logging.error('*palLoad* Palette konnte nicht geladen werden ' + dateiname)
        return False


def tlbLaden():  # Dateiauswahl des zu ladenen Teilbereiches
    file = filedialog.askopenfilename(initialdir="/", title="Teilbereich Oeffnen",
                                      filetypes=(("teilbereich files", "*.teilbereich"), ("all files", "*.*")))
    # Openfiledialog
    if len(file) > 0:
        okay = tlbLoad(file)
        if okay:
            musterDraw()
            tlbDraw()
            messagebox.showinfo('OK', 'Teilbereich wurde geladen!')
        else:
            messagebox.showerror('Fehler', 'Teilbereich konnte nicht geladen werden!')
    return


def tlbLoad(dateiname):  # Teilbereich an aktuelle Position der Box Laden achtet auf Musterrand
    try:
        teilbereich = open(dateiname, 'rb')
        # Teilbereich laden
        box_size = bytes2int(teilbereich.read(2))
        # TLB laden
        for i in range(0, box_size+1):
            y = pos_tlb_y + i
            if y > mus_gy:
                y -= mus_gy+1
            for t in range(0, box_size+1):
                x = pos_tlb_x + t
                if x > mus_gx:
                    x -= mus_gx+1
                muster_feld[x][y] = bytes2int(teilbereich.read(1))
        teilbereich.close()
        logging.info('Teilbereich ' + dateiname + ' wurde geladen.')
        return True
    except IOError:
        logging.error('*tlbLoad* Teilbereich konnte nicht geladen werden ' + dateiname)
        return False


def tlbLadenAlt():  # Dateiauswahl des zu ladenen Teilbereiches Altes Dateiformat
    file = filedialog.askopenfilename(initialdir="/", title="Teilbereich Oeffnen",
                                      filetypes=(("teilbereich files", "*.tlb"), ("all files", "*.*")))
    # Openfiledialog
    if len(file) > 0:
        okay = tlbLoadOld(file)
        if okay:
            musterDraw()
            tlbDraw()
            messagebox.showinfo('OK', 'Teilbereich wurde geladen!')
        else:
            messagebox.showerror('Fehler', 'Teilbereich konnte nicht geladen werden!')
    return


def tlbLoadOld(dateiname):  # Teilbereich an aktuelle Position der Box Laden achtet auf Musterrand; altes Dateiformat
    try:
        teilbereich = open(dateiname, 'rb')
        # Teilbereich laden
        box_size = bytes2int(teilbereich.read(1))
        # TLB laden
        for i in range(0, box_size+1):
            y = pos_tlb_y + i
            if y > mus_gy:
                y -= mus_gy+1
            for t in range(0, box_size+1):
                x = pos_tlb_x + t
                if x > mus_gx:
                    x -= mus_gx+1
                muster_feld[x][y] = bytes2int(teilbereich.read(1))
        teilbereich.close()
        logging.info('Teilbereich ' + dateiname + ' wurde geladen.')
        return True
    except IOError:
        logging.error('*tlbLoadOld* Teilbereich konnte nicht geladen werden ' + dateiname)
        return False


def tlbSpeichern():  # Auswahl des Dateinamens zum Speichern des Teilbereiches
    file = filedialog.asksaveasfilename(initialdir="/", title="Teilbereich Speichern", defaultextension=".teilbereich",
                                        filetypes=(("teilbereich files", "*.teilbereich"), ("all files", "*.*")))
    # Savefiledialog
    if len(file) > 0:
        okay = tlbSave(file)
        if okay:
            messagebox.showinfo('OK', 'Teilbereich wurde gespeichert!')
        else:
            messagebox.showerror('Fehler', 'Teilbereich konnte nicht gesichert werden!')
    return


def tlbSave(dateiname):  # Speichert den Teilbereich
    try:
        teilbereich = open(dateiname, 'wb')
        # Teilbereich größe speichern
        teilbereich.write(tlb_size.to_bytes(length=2, byteorder='little'))
        # Teilbereich speichern
        for i in range(0, tlb_size+1):
            for t in range(0, tlb_size+1):
                teilbereich.write(muster_feld[pos_tlb_x+t][pos_tlb_y+i].to_bytes(length=1, byteorder='big'))
        teilbereich.close()
        logging.info('Teilbereich ' + dateiname + ' wurde gespeichert.')
        return True
    except IOError:
        logging.error('*tlbSave* Teilbereich konnte nicht gespeichert werden ' + dateiname)
        return False


# Funktionen zum Teilbereich Menu
def tlbDrehenLinks():  # Dreht den Teilbereich im gegen den Uhrzeigersinn
    puffer_feld = [[0 for _ in range(tlb_size + 1)] for _ in range(tlb_size + 1)]
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            puffer_feld[t][i] = muster_feld[pos_tlb_x + t][pos_tlb_y + i]

    for i in range(0, tlb_size + 1):
        for t in range(0, tlb_size + 1):
            z = tlb_size - t
            muster_feld[pos_tlb_x + i][pos_tlb_y + z] = puffer_feld[t][i]
    musterDrawTlb()
    tlbDraw()
    return


def tlbDrehenRechts():  # Dreht den Teilbereich im Uhrzeigersinn
    puffer_feld = [[0 for _ in range(tlb_size + 1)] for _ in range(tlb_size + 1)]
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            puffer_feld[t][i] = muster_feld[pos_tlb_x + t][pos_tlb_y + i]
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            z = tlb_size - t
            muster_feld[pos_tlb_x + t][pos_tlb_y + i] = puffer_feld[i][z]
    musterDrawTlb()
    tlbDraw()
    return


def tlbSpiegelnHorizontal():  # Spiegelt den Teilbereich Horizontal
    spiegelnHorizontal(pos_tlb_x, pos_tlb_y, pos_tlb_x + tlb_size, pos_tlb_y + tlb_size)
    musterDrawTlb()
    tlbDraw()
    return


def tlbSpiegelnVertikal():  # Spiegelt den Teilbereich Vertikal
    spiegelnVertikal(pos_tlb_x, pos_tlb_y, pos_tlb_x + tlb_size, pos_tlb_y + tlb_size)
    musterDrawTlb()
    tlbDraw()
    return


def tlbSpiegelnDiagonal():  # Spiegelt den Teilbereich Diagonal
    puffer_feld = [[0 for _ in range(tlb_size + 1)] for _ in range(tlb_size + 1)]
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            puffer_feld[t][i] = muster_feld[pos_tlb_x + t][pos_tlb_y + i]
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            muster_feld[pos_tlb_x + t][pos_tlb_y + i] = puffer_feld[i][t]
    musterDrawTlb()
    tlbDraw()
    return


def tlbSpiegelnDiagonal2():  # Spiegelt den Teilbereich Diagonal
    puffer_feld = [[0 for _ in range(tlb_size + 1)] for _ in range(tlb_size + 1)]
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            puffer_feld[t][i] = muster_feld[pos_tlb_x + t][pos_tlb_y + i]
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            z = tlb_size - t
            p = tlb_size - i
            muster_feld[pos_tlb_x + t][pos_tlb_y + i] = puffer_feld[z][p]
    musterDrawTlb()
    tlbDraw()
    return


def tlbScrollenHoch(pixel=1):  # Scrollt den Teilbereich um x pixel nach oben
    scrollenHoch(pixel, pos_tlb_x, pos_tlb_y, pos_tlb_x + tlb_size, pos_tlb_y + tlb_size)
    musterDrawTlb()
    tlbDraw()
    return


def tlbScrollenRunter(pixel=1):  # Scrollt den Teilbereich um x pixel nach unten
    scrollenRunter(pixel, pos_tlb_x, pos_tlb_y, pos_tlb_x + tlb_size, pos_tlb_y + tlb_size)
    musterDrawTlb()
    tlbDraw()
    return


def tlbScrollenLinks(pixel=1):  # Scrollt den Teilbereich um x pixel nach links
    scrollenLinks(pixel, pos_tlb_x, pos_tlb_y, pos_tlb_x + tlb_size, pos_tlb_y + tlb_size)
    musterDrawTlb()
    tlbDraw()
    return


def tlbScrollenRechts(pixel=1):  # Scrollt den Teilbereich um x pixel nach rechts
    scrollenRechts(pixel, pos_tlb_x, pos_tlb_y, pos_tlb_x + tlb_size, pos_tlb_y + tlb_size)
    musterDrawTlb()
    tlbDraw()
    return


def tlbFarbeLoeschen():  # Setzt all Pixel im Teilbereich auf Hintergrundfarbe die in Vordergrundfarbe sind
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            if muster_feld[pos_tlb_x + t][pos_tlb_y + i] == akt_farbe:
                muster_feld[pos_tlb_x + t][pos_tlb_y + i] = hin_farbe
    tlbDraw()
    musterDrawTlb()
    return


def tlbLoeschen():  # Setzt alle Pixel im Teilbereich auf Hintergrundfarbe
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            muster_feld[pos_tlb_x + t][pos_tlb_y + i] = hin_farbe
    tlbDraw()
    musterDrawTlb()
    return


def tlbFuellen():  # Füllt alle Pixel im Teilbereich die Hintergrundfarbe haben mit der Vordergrundfarbe aus
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            if muster_feld[pos_tlb_x + t][pos_tlb_y + i] == hin_farbe:
                muster_feld[pos_tlb_x + t][pos_tlb_y + i] = akt_farbe
    tlbDraw()
    musterDrawTlb()
    return


def tlbFarbeTauschen():  # tauscht Vorder- mit Hintergrundfarbe im Teilbereich miteinander aus
    for i in range(0, tlb_size+1):
        for t in range(0, tlb_size+1):
            if muster_feld[pos_tlb_x + t][pos_tlb_y + i] == hin_farbe:
                muster_feld[pos_tlb_x + t][pos_tlb_y + i] = akt_farbe
            elif muster_feld[pos_tlb_x + t][pos_tlb_y + i] == akt_farbe:
                muster_feld[pos_tlb_x + t][pos_tlb_y + i] = hin_farbe
    tlbDraw()
    musterDrawTlb()
    return


def tlbUmranden():  # umranden im Teilbereich
    umranden(pos_tlb_x, pos_tlb_y, tlb_size, tlb_size, "tlb")
    musterDrawTlb()
    tlbDraw()
    return


# Funktion für Rechtecke Aktionen im Muster oder Teilbereich
def umranden(x1, y1, x2, y2, mode="muster"):
    # Umranden eines von Pixeln die weder Vordergrundfarbe noch Hintergrundfarbe sind
    # Wenn Pixel weder Vorder- noch Hintergrundfarbe sind, dann im Neuner Feld die Umgebenden Pixel
    # mit Vordergrundfarbe füllen wenn sie auf Hintergrundfarbe stehen
    for i in range(y1 + 1, y1 + y2):  # inneres Feld bei muster ist y1 und x1
        for t in range(x1 + 1, x1 + x2):
            m = muster_feld[t][i]
            if m != hin_farbe and m != akt_farbe:
                if muster_feld[- 1 + t][- 1 + i] == hin_farbe:
                    muster_feld[- 1 + t][- 1 + i] = akt_farbe  # oben links
                if muster_feld[t][- 1 + i] == hin_farbe:
                    muster_feld[t][- 1 + i] = akt_farbe  # oben mitte
                if muster_feld[1 + t][- 1 + i] == hin_farbe:
                    muster_feld[1 + t][- 1 + i] = akt_farbe  # oben rechts
                if muster_feld[- 1 + t][i] == hin_farbe:
                    muster_feld[- 1 + t][i] = akt_farbe  # links
                if muster_feld[1 + t][i] == hin_farbe:
                    muster_feld[1 + t][i] = akt_farbe  # rechts
                if muster_feld[1 + t][1 + i] == hin_farbe:
                    muster_feld[1 + t][1 + i] = akt_farbe  # unten rechts
                if muster_feld[t][1 + i] == hin_farbe:
                    muster_feld[t][1 + i] = akt_farbe  # unten mitte
                if muster_feld[- 1 + t][1 + i] == hin_farbe:
                    muster_feld[- 1 + t][1 + i] = akt_farbe  # unten links
    if mode == "tlb":  # wenn Teilbereich dann jetzt die TLB Position dazu für die Ecken
        y2 += pos_tlb_y
        x2 += pos_tlb_x

    # Ecke links oben
    if muster_feld[x1][y1] != hin_farbe and muster_feld[x1][y1] != akt_farbe:
        if muster_feld[x1 + 1][y1] == hin_farbe:
            muster_feld[x1 + 1][y1] = akt_farbe  # rechts
        if muster_feld[x1 + 1][y1 + 1] == hin_farbe:
            muster_feld[x1 + 1][y1 + 1] = akt_farbe  # unten rechts
        if muster_feld[x1][y1 + 1] == hin_farbe:
            muster_feld[x1][y1 + 1] = akt_farbe  # unten mitte
    # Ecke rechts oben
    if muster_feld[x2][y1] != hin_farbe and \
            muster_feld[x2][y1] != akt_farbe:
        if muster_feld[x2 - 1][y1] == hin_farbe:
            muster_feld[x2 - 1][y1] = akt_farbe  # links
        if muster_feld[x2 - 1][y1 + 1] == hin_farbe:
            muster_feld[x2 - 1][y1 + 1] = akt_farbe  # unten links
        if muster_feld[x2][y1 + 1] == hin_farbe:
            muster_feld[x2][y1 + 1] = akt_farbe  # unten mitte
    # Ecke links unten
    if muster_feld[x1][y2] != hin_farbe and \
            muster_feld[x1][y2] != akt_farbe:
        if muster_feld[x1 + 1][y2] == hin_farbe:
            muster_feld[x1 + 1][y2] = akt_farbe  # rechts
        if muster_feld[x1 + 1][y2 - 1] == hin_farbe:
            muster_feld[x1 + 1][y2 - 1] = akt_farbe  # oben rechts
        if muster_feld[x1][y2 - 1] == hin_farbe:
            muster_feld[x1][y2 - 1] = akt_farbe  # oben mitte
    # Ecke rechts unten
    if muster_feld[x2][y2] != hin_farbe and \
            muster_feld[x2][y2] != akt_farbe:
        if muster_feld[x2 - 1][y2] == hin_farbe:
            muster_feld[x2 - 1][y2] = akt_farbe  # links
        if muster_feld[x2][y2 - 1] == hin_farbe:
            muster_feld[x2][y2 - 1] = akt_farbe  # oben mitte
        if muster_feld[x2 - 1][y2 - 1] == hin_farbe:
            muster_feld[x2 - 1][y2 - 1] = akt_farbe  # oben links
    # Rand  links
    for i in range(y1, y2):
        t = x1
        m = muster_feld[t][i]
        if m != hin_farbe and m != akt_farbe:
            if muster_feld[t][- 1 + i] == hin_farbe:
                muster_feld[t][- 1 + i] = akt_farbe  # oben mitte
            if muster_feld[1 + t][- 1 + i] == hin_farbe:
                muster_feld[1 + t][- 1 + i] = akt_farbe  # oben rechts
            if muster_feld[1 + t][i] == hin_farbe:
                muster_feld[1 + t][i] = akt_farbe  # rechts
            if muster_feld[1 + t][i] == hin_farbe:
                muster_feld[1 + t][1 + i] = akt_farbe  # unten rechts
            if muster_feld[t][1 + i] == hin_farbe:
                muster_feld[t][1 + i] = akt_farbe  # unten mitte
    # Rand rechts
    for i in range(y1, y2):
        t = x2
        m = muster_feld[t][i]
        if m != hin_farbe and m != akt_farbe:
            if muster_feld[-1 + t][- 1 + i] == hin_farbe:
                muster_feld[-1 + t][- 1 + i] = akt_farbe  # oben links
            if muster_feld[t][- 1 + i] == hin_farbe:
                muster_feld[t][- 1 + i] = akt_farbe  # oben mitte
            if muster_feld[-1 + t][i] == hin_farbe:
                muster_feld[-1 + t][i] = akt_farbe  # links
            if muster_feld[t][1 + i] == hin_farbe:
                muster_feld[t][1 + i] = akt_farbe  # unten mitte
            if muster_feld[-1 + t][1 + i] == hin_farbe:
                muster_feld[-1 + t][1 + i] = akt_farbe  # unten links
    # Rand oben
    for t in range(x1, x2):
        i = y1
        m = muster_feld[x1 + t][i]
        if m != hin_farbe and m != akt_farbe:
            if muster_feld[- 1 + t][i] == hin_farbe:
                muster_feld[- 1 + t][i] = akt_farbe  # links
            if muster_feld[1 + t][i] == hin_farbe:
                muster_feld[1 + t][i] = akt_farbe  # rechts
            if muster_feld[1 + t][1 + i] == hin_farbe:
                muster_feld[1 + t][1 + i] = akt_farbe  # unten rechts
            if muster_feld[t][1 + i] == hin_farbe:
                muster_feld[t][1 + i] = akt_farbe  # unten mitte
            if muster_feld[- 1 + t][1 + i] == hin_farbe:
                muster_feld[- 1 + t][1 + i] = akt_farbe  # unten links
    # Rand unten
    for t in range(x1, x2):
        i = y2
        m = muster_feld[t][i]
        if m != hin_farbe and m != akt_farbe:
            if muster_feld[- 1 + t][-1 + i] == hin_farbe:
                muster_feld[- 1 + t][-1 + i] = akt_farbe  # oben links
            if muster_feld[t][-1 + i] == hin_farbe:
                muster_feld[t][-1 + i] = akt_farbe  # oben mitte
            if muster_feld[1 + t][-1 + i] == hin_farbe:
                muster_feld[1 + t][-1 + i] = akt_farbe  # oben rechts
            if muster_feld[- 1 + t][i] == hin_farbe:
                muster_feld[- 1 + t][i] = akt_farbe  # links
            if muster_feld[1 + t][i] == hin_farbe:
                muster_feld[1 + t][i] = akt_farbe  # rechts
    return


def spiegelnHorizontal(x1, y1, x2, y2):  # Spiegelt eine Bereich Horizontal
    starteZeitmessung()
    xspan = x2 - x1
    yspan = y2 - y1
    puffer_feld = [[0 for _ in range(yspan + 1)] for _ in range(xspan + 1)]
    for i in range(0, yspan + 1):
        for t in range(0, xspan + 1):
            puffer_feld[t][i] = muster_feld[x1 + t][y1 + i]
    for i in range(0, yspan + 1):
        c = yspan - i
        for t in range(0, xspan + 1):
            muster_feld[x1 + t][y1 + i] = puffer_feld[t][c]
    stopZeitmessung('Spiegeln Horizontal ' + str(xspan) + "x" + str(yspan))
    return


def spiegelnVertikal(x1, y1, x2, y2):  # Spiegelt eine Bereich Vertikal
    starteZeitmessung()
    xspan = x2 - x1
    yspan = y2 - y1
    puffer_feld = [[0 for _ in range(yspan + 1)] for _ in range(xspan + 1)]  # Comprehensions
    for i in range(0, yspan + 1):
        for t in range(0, xspan + 1):
            puffer_feld[t][i] = muster_feld[x1 + t][y1 + i]
    for i in range(0, yspan + 1):
        for t in range(0, xspan + 1):
            z = xspan - t
            muster_feld[x1 + t][y1 + i] = puffer_feld[z][i]
    stopZeitmessung('Spiegeln Vertikal ' + str(xspan) + "x" + str(yspan))
    return


def scrollenHoch(pixel, x1, y1, x2, y2):  # Scrollt einen Bereich um x pixel nach oben
    starteZeitmessung()
    xspan = x2 - x1
    yspan = y2 - y1
    if pixel == 1:
        puffer = [0 for _ in range(0, xspan + 1)]  # Comprehensions
        for i in range(0, xspan + 1):
            puffer[i] = muster_feld[x1 + i][y1]
        for i in range(1, yspan + 1):  # ganze feld 1 nach oben
            for t in range(0, xspan + 1):
                muster_feld[x1 + t][y1 + i - 1] = muster_feld[x1 + t][y1 + i]
        for i in range(0, xspan + 1):
            muster_feld[x1 + i][y2] = puffer[i]
    else:
        puffer = [[0 for _ in range(0, pixel)]for _ in range(0, xspan + 1)]
        for i in range(0, xspan + 1):    # Wegpacken der oberen Pixel Zeilen
            for t in range(0, pixel):
                puffer[i][t] = muster_feld[x1 + i][y1 + t]
        for i in range(0, xspan + 1):    # Ganze Rest feld um Pixel nach oben
            z = 0
            for t in range(pixel, yspan + 1):
                muster_feld[x1 + i][y1 + z] = muster_feld[x1 + i][y1 + t]
                z += 1
        for i in range(0, xspan + 1):      # gepufferte Daten zurückschreiben nach unten
            z = 0
            for t in range(yspan + 1 - pixel, yspan + 1):
                muster_feld[x1 + i][y1 + t] = puffer[i][z]
                z += 1
    stopZeitmessung('Hoch Scrollen ' + str(pixel) + ' Pixel' + str(x2-x1) + 'x' + str(y2-y1))
    return


def scrollenRunter(pixel, x1, y1, x2, y2):  # Scrollt einen Bereich um x pixel nach unten
    starteZeitmessung()
    xspan = x2 - x1
    yspan = y2 - y1
    if pixel == 1:
        puffer = [0 for _ in range(0, xspan + 1)]  # Comprehensions
        for i in range(0, xspan + 1):
            puffer[i] = muster_feld[x1 + i][y2]
        for i in range(yspan - 1, 0-1, -1):
            for t in range(0, xspan + 1):
                muster_feld[x1 + t][y1 + i + 1] = muster_feld[x1 + t][y1 + i]
        for i in range(0, xspan + 1):
            muster_feld[x1 + i][y1] = puffer[i]
    else:
        puffer = [[0 for _ in range(0, pixel)] for _ in range(0, xspan + 1)]
        for i in range(0, xspan + 1):    # Wegpacken unteren Pixel Zeilen
            z = 0
            for t in range(yspan + 1 - pixel, yspan + 1):
                puffer[i][z] = muster_feld[x1 + i][y1 + t]
                z += 1
        for i in range(yspan - pixel, -1, -1):  # ganze feld pixel nach unten
            for t in range(0, xspan + 1):
                muster_feld[x1 + t][y1 + i + pixel] = muster_feld[x1 + t][y1 + i]
        for i in range(0, xspan + 1):      # gepufferte Daten zurückschreiben nach oben
            z = 0
            for t in range(0, pixel):
                muster_feld[x1 + i][y1 + t] = puffer[i][t]
                z += 1
    stopZeitmessung('Runter Scrollen ' + str(pixel) + ' Pixel ' + str(xspan) + 'x' + str(yspan))
    return


def scrollenLinks(pixel, x1, y1, x2, y2):  # Scrollt einen Bereich um x pixel nach links
    starteZeitmessung()
    xspan = x2 - x1
    yspan = y2 - y1
    if pixel == 1:
        puffer = [0 for _ in range(0, yspan + 1)]  # Comprehensions
        for i in range(0, yspan + 1):
            puffer[i] = muster_feld[x1][y1 + i]
        for i in range(1, xspan + 1):
            for t in range(0, yspan + 1):
                muster_feld[x1 + i - 1][y1 + t] = muster_feld[x1 + i][y1 + t]
        for i in range(0, yspan + 1):
            muster_feld[x2][y1 + i] = puffer[i]
    else:
        puffer = [[0 for _ in range(0, pixel)] for _ in range(0, yspan + 1)]
        for i in range(0, yspan + 1):    # Wegpacken der linken Pixel Zeilen
            for t in range(0, pixel):
                puffer[i][t] = muster_feld[x1 + t][i]
        for i in range(pixel, xspan + 1):
            for t in range(0, yspan + 1):
                muster_feld[x1 + i - pixel][y1 + t] = muster_feld[x1 + i][y1 + t]
        for i in range(0, yspan + 1):    # W
            z = 0
            for t in range(xspan + 1 - pixel, xspan + 1):
                muster_feld[x1 + t][y1 + i] = puffer[i][z]
                z += 1
    stopZeitmessung('Links scrollen ' + str(pixel) + ' Pixel' + str(xspan) + 'x' + str(yspan))
    return


def scrollenRechts(pixel, x1, y1, x2, y2):  # Scrollt einen Bereich um x pixel nach rechts
    starteZeitmessung()
    xspan = x2 - x1
    yspan = y2 - y1
    if pixel == 1:
        puffer = [0 for _ in range(0, yspan + 1)]  # Comprehensions
        for i in range(0, yspan + 1):
            puffer[i] = muster_feld[x2][y1 + i]
        for i in range(xspan - 1, 0-1, -1):
            for t in range(0, yspan + 1):
                muster_feld[x1 + i + 1][y1 + t] = muster_feld[x1 + i][y1 + t]
        for i in range(0, yspan + 1):
            muster_feld[x1][y1 + i] = puffer[i]
    else:
        puffer = [[0 for _ in range(0, pixel)] for _ in range(0, yspan + 1)]
        for i in range(0, yspan + 1):    # Wegpacken der rechte Pixel Zeilen
            z = 0
            for t in range(xspan + 1 - pixel, xspan + 1):
                puffer[i][z] = muster_feld[x1 + t][y1 + i]
                z += 1
        for i in range(xspan - pixel, 0-1, -1):
            for t in range(0, yspan + 1):
                muster_feld[x1 + i + pixel][y1 + t] = muster_feld[x1 + i][y1 + t]
        for i in range(0, yspan + 1):      # gepufferte Daten zurückschreiben nach ganz links
            for t in range(0, pixel):
                muster_feld[x1 + t][y1 + i] = puffer[i][t]
    stopZeitmessung('scrollen Rechts scrollen ' + str(pixel) + ' Pixel' + str(xspan) + 'x' + str(yspan))
    return


# Funktionen zum Muster Menu
def musterSpiegelnHorizontal():  # Spiegeln des Musters in der Horizontalen
    spiegelnHorizontal(0, 0, mus_gx, mus_gy)
    musterDraw()
    tlbDraw()
    return


def musterSpiegelnVertikal():  # Spiegeln des Musters in der Vertikalen
    spiegelnVertikal(0, 0, mus_gx, mus_gy)
    musterDraw()
    tlbDraw()
    return


def musterScrollenHoch(pixel=1):  # Scrollen des Musters nach oben um x pixel
    scrollenHoch(pixel, 0, 0, mus_gx, mus_gy)
    musterDraw()
    tlbDraw()
    return


def musterScrollenRunter(pixel=1):  # Scrollen des Musters nach unten um x pixel
    scrollenRunter(pixel, 0, 0, mus_gx, mus_gy)
    musterDraw()
    tlbDraw()
    return


def musterScrollenLinks(pixel=1):  # Scrollen des Musters nach links um x pixel
    scrollenLinks(pixel, 0, 0, mus_gx, mus_gy)
    musterDraw()
    tlbDraw()
    return


def musterScrollenRechts(pixel=1):  # Scrollen des Musters nach rechts um x pixel
    scrollenRechts(pixel, 0, 0, mus_gx, mus_gy)
    musterDraw()
    tlbDraw()
    return


def musterFarbeLoeschen():  # Setzt die Vordergrundfarbe auf die Hintergrundfarbe im ganzen Muster
    starteZeitmessung()
    global muster_feld
    for i in range(0, mus_gy+1):
        for t in range(0, mus_gx+1):
            if muster_feld[t][i] == akt_farbe:
                muster_feld[t][i] = hin_farbe
    stopZeitmessung('Muster Farbe loeschen')
    tlbAktReDraw(hin_farbe)
    musterAktReDraw(hin_farbe)
    return


def musterLoeschen():  # Setzt alle Pixel des Musters auf Hintergrundfarbe
    starteZeitmessung()
    global muster_feld
    for i in range(0, mus_gy+1):
        for t in range(0, mus_gx+1):
            muster_feld[t][i] = hin_farbe
    stopZeitmessung('Muster loeschen')
    tlbDraw()
    musterAktReDraw(hin_farbe)
    return


def musterFuellen():  # Füllt alls Pixel im Muster mit der Vordergrundfarbe aus die in Hintegrundfarbe sind
    starteZeitmessung()
    global muster_feld
    for i in range(0, mus_gy+1):
        for t in range(0, mus_gx+1):
            if muster_feld[t][i] == hin_farbe:
                muster_feld[t][i] = akt_farbe
    stopZeitmessung('Muster fuellen')
    tlbAktReDraw()
    musterAktReDraw()
    return


def musterFarbeTauschen():  # Tauscht Vorder- und Hintergrundfarbe im Muster miteinander aus
    starteZeitmessung()
    global muster_feld
    for i in range(0, mus_gy+1):
        for t in range(0, mus_gx+1):
            if muster_feld[t][i] == hin_farbe:
                muster_feld[t][i] = akt_farbe
            elif muster_feld[t][i] == akt_farbe:
                muster_feld[t][i] = hin_farbe
    stopZeitmessung('Muster Farbe tauschen')
    tlbAktReDraw()
    tlbAktReDraw(hin_farbe)
    musterAktReDraw(akt_farbe)
    musterAktReDraw(hin_farbe)
    return


def musterUmranden():  # Menüpunkt zur Farblichen Umrandung des Musters
    starteZeitmessung()
    umranden(0, 0, mus_gx, mus_gy)
    stopZeitmessung('Muster Farbe umranden')
    musterAktReDraw()
    tlbAktReDraw()
    return


# Funktionen zum Export Menu
def musterAlsCArray():  # Stellt das Muster als C# Array in neuem Fenster zum Kopieren bereit
    unterfenster = Tk()
    unterfenster.title('Export C# Array')
    ausgabe = ScrolledText(unterfenster, bg="white", width=50, height=20, font="Arial 10")
    ausgabe.insert('end', "byte[,] muster = new byte[" + str(mus_gx+1) + "," + str(mus_gy+1) + "] ")
    ausgabe.insert('end', "\n{")
    for i in range(0, mus_gy+1):
        ausgabe.insert('end', "\n{ ")
        for t in range(0, mus_gx+1):
            ausgabe.insert('end', "0x" + format(muster_feld[t][i], '02x'))
            if t != mus_gx:
                ausgabe.insert('end', ", ")
            else:
                ausgabe.insert('end', " ")
        if i != mus_gy:
            ausgabe.insert('end', "},")
        else:
            ausgabe.insert('end', "}")
    ausgabe.insert('end', "\n};\n")
    ausgabe.pack()
    unterfenster.mainloop()
    return


def tlbAlsCArray():  # Stellt den Teilbereich als C# Array in neuem Fenster zum Kopieren bereit
    unterfenster = Tk()
    unterfenster.title('Export C# Array')
    ausgabe = ScrolledText(unterfenster, bg="white", width=50, height=20, font="Arial 10")
    ausgabe.insert('end', "byte[,] muster = new byte[" + str(tlb_size+1) + "," + str(tlb_size+1) + "] ")
    ausgabe.insert('end', "\n{")
    for i in range(pos_tlb_y, pos_tlb_y + tlb_size+1):
        ausgabe.insert('end', "\n{ ")
        for t in range(pos_tlb_x, pos_tlb_x+tlb_size+1):
            ausgabe.insert('end', "0x" + format(muster_feld[t][i], '02x'))
            if t != pos_tlb_x + tlb_size:
                ausgabe.insert('end', ", ")
            else:
                ausgabe.insert('end', " ")
        if i == pos_tlb_y + tlb_size:
            ausgabe.insert('end', "}\n")
        else:
            ausgabe.insert('end', "},")
    ausgabe.insert('end', "};\n")
    ausgabe.pack()
    unterfenster.mainloop()
    return


def palAlsCArray():  # Stellt die Palette als C# Array in neuem Fenster zum Kopieren bereit
    unterfenster = Tk()
    unterfenster.title('Export C# Array')
    ausgabe = ScrolledText(unterfenster, bg="white", width=50, height=20, font="Arial 10")
    ausgabe.insert('end', "byte[] vga_color_red = new byte[256] ")
    ausgabe.insert('end', "{ ")
    for i in range(0, 256):
        ausgabe.insert('end', "0x" + format(vga_pal_rot[i], '02x'))
        if i != 255:
            ausgabe.insert('end', ", ")
        else:
            ausgabe.insert('end', " ")
    ausgabe.insert('end', "};\n")
    ausgabe.insert('end', "byte[] vga_color_green = new byte[256] ")
    ausgabe.insert('end', "{ ")
    for i in range(0, 256):
        ausgabe.insert('end', "0x" + format(vga_pal_gruen[i], '02x'))
        if i != 255:
            ausgabe.insert('end', ", ")
        else:
            ausgabe.insert('end', " ")
    ausgabe.insert('end', "};\n")
    ausgabe.insert('end', "byte[] vga_color_blue = new byte[256] ")
    ausgabe.insert('end', "{ ")
    for i in range(0, 256):
        ausgabe.insert('end', "0x" + format(vga_pal_blau[i], '02x'))
        if i != 255:
            ausgabe.insert('end', ", ")
        else:
            ausgabe.insert('end', " ")
    ausgabe.insert('end', "};\n")
    ausgabe.pack()
    unterfenster.mainloop()


def musterAlsPng(transparent=True):  # Auswahl des Dateinamen für die Speicherung des Musters als PNG
    file = filedialog.asksaveasfilename(initialdir="/", title="Export Muster als Portable Network Grafik",
                                        defaultextension=".png",
                                        filetypes=(("PNG files", "*.png"), ("all files", "*.*")))
    # Savefiledialog
    if len(file) > 0:
        okay = musterAlsPngSave(file, transparent)
        if okay:
            messagebox.showinfo('OK', 'PNG wurde erzeugt!')
        else:
            messagebox.showerror('Fehler', 'PNG konnte nicht erzeugt werden!')
    return


def musterAlsPngSave(dateiname, transparent):  # Speichert das Muster als PNG mit/ohne Hintergrundfarbe als Transparenz
    try:
        img = Image.new('RGB', (mus_gx+1, mus_gy+1), (255, 255, 255))
        mask = None
        if transparent:
            mask = Image.new('L', img.size, 255)
        for i in range(0, mus_gx+1):
            for t in range(0, mus_gy+1):
                img.putpixel((i, t), (vga_pal_rot[muster_feld[i][t]],
                                      vga_pal_gruen[muster_feld[i][t]],
                                      vga_pal_blau[muster_feld[i][t]]))
                if muster_feld[i][t] == hin_farbe and transparent:
                    mask.putpixel((i, t), 0)
        if transparent:
            img.putalpha(mask)
        img.save(dateiname, "PNG")
        logging.info('Muster wurde als PNG ' + dateiname + ' gespeichert')
        return True
    except IOError:
        writeToLog('Muster konnte nicht gespeichert werden IOError')
        logging.error('Muster konnte nicht als PNG gespeichert werden ' + dateiname)
        return False


def tlbAlsIcoImage(transparent=True):  # Auswahl des Dateinamen für die Speicherung des Tlb als PNG
    # Checken ob die Boxgroesse = Ico Standard wenn nicht Warnung und speichern abbrechen
    if tlb_size + 1 not in (16, 24, 32, 48, 64, 128, 256):
        messagebox.showerror('Fehler', 'Boxsize entspricht nicht einer der erforderlichen Standardgroessen'
                                       ' (16x16,24x24,32x32,48x48,64x64,128x128,256x256)')
        return
    file = filedialog.asksaveasfilename(initialdir="/", title="Export Teilbereich als Microsoft Icon",
                                        defaultextension=".ico",
                                        filetypes=(("Icon files", "*.ico"), ("all files", "*.*")))
    # Savefiledialog
    if len(file) > 0:
        okay = tlbAlsIcoSave(file, transparent, False)
        if okay:
            messagebox.showinfo('OK', 'ico wurde erzeugt!')
        else:
            messagebox.showerror('Fehler', 'Icon konnte nicht erzeugt werden!')
    return


def tlbAlsIcoImageMul(transparent=True):  # Auswahl des Dateinamen für die Speicherung des Tlb als ico Multi
    # Checken ob die Boxgroesse = Ico Standard wenn nicht Warnung und speichern abbrechen
    if tlb_size + 1 not in (16, 24, 32, 48, 64, 128, 256):
        messagebox.showerror('Fehler', 'Boxsize entspricht nicht einer der erforderlichen Standardgroessen'
                                       ' (16x16,24x24,32x32,48x48,64x64,128x128,256x256)')
        return
    file = filedialog.asksaveasfilename(initialdir="/", title="Export Teilbereich als Microsoft MultisizeIcon",
                                        defaultextension=".ico",
                                        filetypes=(("Icon files", "*.ico"), ("all files", "*.*")))
    # Savefiledialog
    if len(file) > 0:
        okay = tlbAlsIcoSave(file, transparent, True)
        if okay:
            messagebox.showinfo('OK', 'ico wurde erzeugt!')
        else:
            messagebox.showerror('Fehler', 'Icon konnte nicht erzeugt werden!')
    return


def tlbAlsIcoSave(dateiname, transparent, multi):
    # Speichert den Tlb als Icon mit/ohne Hintergrund Farbe als Transparenzwert sowie mehrere Auflösungen
    try:
        img = Image.new('RGB', (tlb_size + 1, tlb_size + 1), (255, 255, 255))
        mask = None
        if transparent:
            mask = Image.new('L', img.size, 255)
        for i in range(0, tlb_size + 1):
            for t in range(0, tlb_size + 1):
                img.putpixel((i, t), (vga_pal_rot[muster_feld[pos_tlb_x + i][pos_tlb_y + t]],
                                      vga_pal_gruen[muster_feld[pos_tlb_x + i][pos_tlb_y + t]],
                                      vga_pal_blau[muster_feld[pos_tlb_x + i][pos_tlb_y + t]]))
                if muster_feld[i][t] == hin_farbe and transparent:
                    mask.putpixel((i, t), 0)
        if transparent:
            img.putalpha(mask)
        if multi:
            icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        else:
            icon_sizes = [(tlb_size + 1, tlb_size + 1)]
        img.save(dateiname, "ico", sizes=icon_sizes)
        logging.info('Teilbereich wurde als Icon ' + dateiname + ' gespeichert')
        return True
    except IOError:
        writeToLog('Teilbereich konnte nicht gespeichert werden IOError')
        logging.error('Teilbereich konnte nicht als ico gespeichert werden ' + dateiname)
        return False


def tlbAlsPng(transparent=True):  # Auswahl des Dateinamen für die Speicherung des Tlb als PNG
    file = filedialog.asksaveasfilename(initialdir="/", title="Export Teilbereich als Portable Network Grafik",
                                        defaultextension=".png",
                                        filetypes=(("PNG files", "*.png"), ("all files", "*.*")))
    # Savefiledialog
    if len(file) > 0:
        okay = tlbAlsPngSave(file, transparent)
        if okay:
            messagebox.showinfo('OK', 'PNG wurde erzeugt!')
        else:
            messagebox.showerror('Fehler', 'PNG konnte nicht erzeugt werden!')
    return


def tlbAlsPngSave(dateiname, transparent):  # Speichert den Tlb als PNG mit/ohne Hintergrund Farbe als Transparenzwert
    try:
        img = Image.new('RGB', (tlb_size + 1, tlb_size + 1), (255, 255, 255))
        mask = None
        if transparent:
            mask = Image.new('L', img.size, 255)
        for i in range(0, tlb_size + 1):
            for t in range(0, tlb_size + 1):
                img.putpixel((i, t), (vga_pal_rot[muster_feld[pos_tlb_x + i][pos_tlb_y + t]],
                                      vga_pal_gruen[muster_feld[pos_tlb_x + i][pos_tlb_y + t]],
                                      vga_pal_blau[muster_feld[pos_tlb_x + i][pos_tlb_y + t]]))
                if muster_feld[i][t] == hin_farbe and transparent:
                    mask.putpixel((i, t), 0)
        if transparent:
            img.putalpha(mask)
        img.save(dateiname, "PNG")
        logging.info('Teilbereich wurde als PNG ' + dateiname + ' gespeichert')
        return True
    except IOError:
        writeToLog('Teilbereich konnte nicht gespeichert werden IOError')
        logging.error('Teilbereich konnte nicht als PNG gespeichert werden ' + dateiname)
        return False


def musterFuerCSSBase64Image():  # Gibt das Muster Base64 CSS Format zum Kopieren in neues Fenster aus
    unterfenster = Tk()
    unterfenster.title('Export URL base64 fuer CSS')
    img = Image.new('RGB', (mus_gx + 1, mus_gy + 1), (255, 255, 255))
    mask = Image.new('L', img.size, 255)
    for i in range(0, mus_gx + 1):
        for t in range(0, mus_gy + 1):
            img.putpixel((i, t),
                         (vga_pal_rot[muster_feld[i][t]],
                          vga_pal_gruen[muster_feld[i][t]],
                          vga_pal_blau[muster_feld[i][t]]))
            if muster_feld[i][t] == hin_farbe:
                mask.putpixel((i, t), 0)
    img.putalpha(mask)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    mein_image = buffer.getvalue()

    ausgabe = ScrolledText(unterfenster, bg="white", width=50, height=20, font="Arial 10")
    ausgabe.pack()
    encoded_string = b64encode(mein_image)
    ausgabe.insert('end', ".myMuster{ background:url(data:image/png;base64,")
    ausgabe.insert('end', encoded_string)
    ausgabe.insert('end', ") repeat;")
    ausgabe.insert('end', "}")
    unterfenster.mainloop()
    return


def tlbFuerCSSBase64Image():  # Gibt den Teilbereich Base64 CSS Format zum Kopieren in neues Fenster aus
    unterfenster = Tk()
    unterfenster.title('Export URL base64 fuer CSS')
    img = Image.new('RGB', (tlb_size + 1, tlb_size + 1), (255, 255, 255))
    mask = Image.new('L', img.size, 255)
    for i in range(0, tlb_size + 1):
        for t in range(0, tlb_size + 1):
            img.putpixel((i, t),
                         (vga_pal_rot[muster_feld[pos_tlb_x + i][pos_tlb_y + t]],
                          vga_pal_gruen[muster_feld[pos_tlb_x + i][pos_tlb_y + t]],
                          vga_pal_blau[muster_feld[pos_tlb_x + i][pos_tlb_y + t]]))
            if muster_feld[i][t] == hin_farbe:
                mask.putpixel((i, t), 0)
    img.putalpha(mask)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    mein_image = buffer.getvalue()

    ausgabe = ScrolledText(unterfenster, bg="white", width=50, height=20, font="Arial 10")
    ausgabe.pack()
    encoded_string = b64encode(mein_image)
    ausgabe.insert('end', ".myMuster{ background:url(data:image/png;base64,")
    ausgabe.insert('end', encoded_string)
    ausgabe.insert('end', ") repeat;")
    ausgabe.insert('end', "}")
    unterfenster.mainloop()
    return


def musterAlsHTML():  # Auswahl des Dateinamens für die Ausgabe als HTML Datei
    file = filedialog.asksaveasfilename(initialdir="/", title="Export Muster als HTML", defaultextension=".html",
                                        filetypes=(("html files", "*.html"), ("all files", "*.*")))
    # Savefiledialog
    if len(file) > 0:
        okay = musterAlsHTMLExport(file)
        if okay:
            messagebox.showinfo('OK', 'HTML wurde erzeugt!')
        else:
            messagebox.showerror('Fehler', 'HTML konnte nicht erzeugt werden!')
    return


def musterAlsHTMLExport(dateiname):  # Ausgabe des Musters in eine HTML Datei
    try:
        html_file = open(dateiname, 'w')
        # Kopf
        html_file.write('<html><head>')
        # Javascript
        html_file.write('<script type=\"text/javascript\">\nfunction hervorheben(klasse)\n{\n')
        html_file.write('  var elemente = document.getElementsByClassName(klasse);\n')
        html_file.write('  for(i=0;i<elemente.length;i++)\n  {\n  	elemente[i].style.borderColor =\"black\";\n  }')
        html_file.write('\n}\nfunction normal(klasse)\n{\n  var elemente = document.getElementsByClassName(klasse);\n')
        html_file.write('  for(i=0;i<elemente.length;i++)\n  {\n')
        html_file.write('  	elemente[i].style.borderColor =\"white\";\n  }\n}\n</script>\n')
        # Css Style
        html_file.write('<style type=\"text/css\">\n')
        html_file.write("td { border-color:white; border-width: 2px; border-style: solid;}\n")
        html_file.write(".ft { border-color:black; border-width: 2px; border-style: solid;}\n")
        # Farbe definieren im Style Sheet
        for i in range(0, 256):
            html_file.write('.farbe' + str(i))
            nfarbe = "#" + format(vga_pal_rot[i], '02x') + format(vga_pal_gruen[i], '02x') +\
                     format(vga_pal_blau[i], '02x')
            html_file.write(' { background-color: ' + nfarbe)
            html_file.write(';width:20px;height:20px; }\n')
        # style schliessen und weitere
        html_file.write('</style>\n</head>\n<body>\n<table>\n')
        farbenzaehler = [0]  # Knoten farben mit zählen
        for i in range(1, 256):
            farbenzaehler.append(0)
        for zeile in range(0, mus_gy+1):
            html_file.write('<tr>\n')  # Zeile in tabelle öffnen
            for spalte in range(0, mus_gx+1):
                html_file.write('<td class=\"farbe')
                html_file.write(str(muster_feld[spalte][zeile]))
                html_file.write('\" title=\"farbe ')
                html_file.write('\">&nbsp</td>\n')  # mit Inhalt sonst keinen Rahmen Element fertig
                farbenzaehler[muster_feld[spalte][zeile]] += 1
            html_file.write('</tr>\n')  # Tabellenzeile abschliessen
        html_file.write('</table>\n')  # Muster fertig
        html_file.write('<table>\n')  # Farbzähler report erzeugen
        t = 1
        for x in range(0, 256):
            if (t // 16 == 0 and t > 15) or x == 0:
                html_file.write('<tr>\n')
            if farbenzaehler[x] > 0:
                html_file.write('<td class=\"farbe' + str(x))
                html_file.write('\" onclick=\"hervorheben(\'farbe' + str(x))
                html_file.write('\')\" ondblclick=\"normal(\'farbe' + str(x))
                html_file.write('\')\">&nbsp</td>\n')
                html_file.write('<td class=\"ft\">Farbe ' + str(x) + " = " + str(farbenzaehler[x]) + " Knoten</td>\n")
                t += 1
            if (t // 16 == 0 and t > 15) or x == 255:
                html_file.write('</tr>\n')
        html_file.write('</table>\n</body>\n</html>')  # Html zumachen
        html_file.close()
        logging.info('HTML ' + dateiname + ' vom Muster wurde erzeugt.')
        return True
    except IOError:
        writeToLog('Muster konnte nicht exportiert werden IOError')
        logging.error('HTML vom Muster konnte nicht erzeugt werden ' + dateiname)
        return False


def boxSet(size):  # setzt die Box Größe nach Menü auswahl passt auf das die Box nicht grösser als das Muster wird
    global tlb_size
    if mus_gx < size or mus_gy < size:
        messagebox.showinfo('Warnung', 'Box darf nicht groesser als das Muster werden!')
        return
    tlb_size = size
    tlbDraw()
    setBox()
    box_bewegen(0, 0)  # ausrichten der Box
    set_sb_tlb()
    return


def resetBox():  # setz die Box auf Standardgrösse z.B. nach dem Laden eines Musters
    global pos_tlb_y, pos_tlb_x, tlb_size
    pos_tlb_x = 0
    pos_tlb_y = 0
    tlb_size = tlb_anzahl_felder-1
    setBox()
    set_sb_tlb()
    return


def musterSet(size):  # dient zum leichteren Setzen der Mustergröße über das Menü
    global mus_gx, mus_gy
    if size == 319:
        mus_gx = 319
        mus_gy = 255
    else:
        mus_gy = size
        mus_gx = size
    resetBox()
    return


def tlbInit():  # Objekte für den Teilbereich initialisieren und ausrichten
    # Tlb Elemente erzeugen
    global tlb  # element1
    # weitere tlb an liste
    for i in range(0, tlb_size + 1):
        for t in range(0, tlb_size + 1):
            if i == 0 and t == 0:
                pass  # übergehe bereits erzeugtes erstes element
            else:
                tlb.append(TlbRec(teilbereichCanvas, "Tx" + str(i) + "y" + str(t)))
    # tlb einstellen
    t = 0
    z = 0
    for i in tlb:
        i.setSize(tlb_rec_size)
        i.setPosX(t * tlb_feld_size + 1)
        i.setPosY(z * tlb_feld_size + 1)
        i.setColorRGB(20, t * 10, z * 10)
        t += 1
        if t == tlb_size + 1:
            t = 0
            z += 1
    for i in tlb:
        i.drawME()
    return


def palInit():  # Objekte für die Farbpalette initialisieren und ausrichten
    global pal
    for i in range(0, 16):
        for t in range(0, 16):
            if i == 0 and t == 0:
                pass  # übergehe bereits erzeugtes erstes element
            else:
                pal.append(PalRec(palCanvas, "Fx" + str(i) + "y" + str(t)))
    t = 0
    z = 0
    k = 0
    for i in pal:
        i.setSize(farb_feld_size)
        i.setPosX(t * farb_feld_size)
        i.setPosY(z * farb_feld_size)
        i.setColorRGB(vga_pal_rot[k], vga_pal_gruen[k], vga_pal_blau[k])
        t += 1
        k += 1
        if t == 16:
            t = 0
            z += 1
    pal[0].select()
    pal[0].xcross(False)
    pal[1].select()
    pal[1].xcross(True)
    for i in pal:
        i.drawME()
    return


def programmBeenden():  # Beendung des Programms
    antwort = messagebox.askokcancel('Programm beenden?', 'Beenden vom Muster Editor')
    if antwort == 1:
        hauptfenster.destroy()
        logging.info('MusterEditor beendet')
        logging.shutdown()
        sys.exit(0)
    return


def menueInit():  # Menu definieren
    leiste = Menu(hauptfenster)
    hauptfenster.config(menu=leiste)
    # Untermenue Datei
    datei_menu = Menu(leiste)
    leiste.add_cascade(label="Datei", menu=datei_menu)
    datei_menu.add_command(label="Neu...", command=musterNeu)
    datei_menu.add_separator()
    datei_menu.add_command(label="Muster Laden", command=musterLaden)
    datei_menu.add_command(label="Muster Speichern", command=musterSpeichern)
    datei_menu.add_separator()
    datei_menu.add_command(label="Farbpalette Laden", command=palLaden)
    datei_menu.add_command(label="Farbpalette Speichern", command=palSpeichern)
    datei_menu.add_separator()
    datei_menu.add_command(label="Teilbereich Laden", command=tlbLaden)
    datei_menu.add_command(label="Teilbereich Speichern", command=tlbSpeichern)
    datei_menu.add_separator()
    datei_menu.add_command(label="PNG in das Muster Laden", command=pngLaden)
    datei_menu.add_command(label="PNG (Alpha Blending) in das Muster Laden", command=pngAlphaLaden)
    datei_menu.add_command(label="Altes Muster Laden", command=musterAltLaden)
    datei_menu.add_command(label="Farbpalette Alt Laden", command=palLadenAlt)
    datei_menu.add_command(label="Alten Teilbereich Laden", command=tlbLadenAlt)
    datei_menu.add_separator()
    datei_menu.add_command(label="Beenden", command=programmBeenden, accelerator="Alt+q")

    # Untermenu Teilbereich
    teilbereich_menu = Menu(leiste)
    leiste.add_cascade(label="Teilbereich", menu=teilbereich_menu)
    teilbereich_menu.add_command(label="Drehen Links", command=tlbDrehenLinks)
    teilbereich_menu.add_command(label="Drehen Rechts", command=tlbDrehenRechts)
    teilbereich_menu.add_separator()
    teilbereich_menu.add_command(label="Spiegeln Horizontal", command=tlbSpiegelnHorizontal)
    teilbereich_menu.add_command(label="Spiegeln Vertikal", command=tlbSpiegelnVertikal)
    teilbereich_menu.add_command(label="Spiegeln Diagonal", command=tlbSpiegelnDiagonal)
    teilbereich_menu.add_command(label="Spiegeln Diagonal2", command=tlbSpiegelnDiagonal2)
    teilbereich_menu.add_separator()
    teilbereich_menu.add_command(label="Scrollen Hoch", command=tlbScrollenHoch)
    teilbereich_menu.add_command(label="Scrollen Runter", command=tlbScrollenRunter)
    teilbereich_menu.add_command(label="Scrollen Links", command=tlbScrollenLinks)
    teilbereich_menu.add_command(label="Scrollen Rechts", command=tlbScrollenRechts)
    teilbereich_menu.add_command(label="Scrollen 10 px Hoch", command=lambda: tlbScrollenHoch(10))
    teilbereich_menu.add_command(label="Scrollen 10 px Runter", command=lambda: tlbScrollenRunter(10))
    teilbereich_menu.add_command(label="Scrollen 10 px Links", command=lambda: tlbScrollenLinks(10))
    teilbereich_menu.add_command(label="Scrollen 10 px Rechts", command=lambda: tlbScrollenRechts(10))
    teilbereich_menu.add_separator()
    teilbereich_menu.add_command(label="Farbe Loeschen", command=tlbFarbeLoeschen)
    teilbereich_menu.add_command(label="Loeschen", command=tlbLoeschen)
    teilbereich_menu.add_command(label="Fuellen", command=tlbFuellen)
    teilbereich_menu.add_command(label="Farbe Tauschen", command=tlbFarbeTauschen)
    teilbereich_menu.add_command(label="Umranden", command=tlbUmranden)

    # Untermenu Muster
    muster_menu = Menu(leiste)
    leiste.add_cascade(label="Muster", menu=muster_menu)
    muster_menu.add_command(label="Spiegeln Horizontal", command=musterSpiegelnHorizontal)
    muster_menu.add_command(label="Spiegeln Vertikal", command=musterSpiegelnVertikal)
    muster_menu.add_separator()
    muster_menu.add_command(label="Scrollen Hoch", command=musterScrollenHoch)
    muster_menu.add_command(label="Scrollen Runter", command=musterScrollenRunter)
    muster_menu.add_command(label="Scrollen Links", command=musterScrollenLinks)
    muster_menu.add_command(label="Scrollen Rechts", command=musterScrollenRechts)
    muster_menu.add_command(label="Scrollen 10 px Hoch", command=lambda: musterScrollenHoch(10))
    muster_menu.add_command(label="Scrollen 10 px Runter", command=lambda: musterScrollenRunter(10))
    muster_menu.add_command(label="Scrollen 10 px Links", command=lambda: musterScrollenLinks(10))
    muster_menu.add_command(label="Scrollen 10 px Rechts", command=lambda: musterScrollenRechts(10))
    muster_menu.add_separator()
    muster_menu.add_command(label="Farbe Loeschen", command=musterFarbeLoeschen)
    muster_menu.add_command(label="Loeschen", command=musterLoeschen)
    muster_menu.add_command(label="Fuellen", command=musterFuellen)
    muster_menu.add_command(label="Farbe Tauschen", command=musterFarbeTauschen)
    muster_menu.add_command(label="Umranden", command=musterUmranden)

    # Untermenu Box
    groessen_menu = Menu(leiste)
    leiste.add_cascade(label="Groessen", menu=groessen_menu)
    groessen_menu.add_command(label="Box Groesse +1", command=boxSetPlus1, accelerator="+")
    groessen_menu.add_command(label="Box Groesse -1", command=boxSetMinus1, accelerator="-")
    groessen_menu.add_command(label="Box   16*16", command=lambda: boxSet(15))
    groessen_menu.add_command(label="Box   24*24", command=lambda: boxSet(23))
    groessen_menu.add_command(label="Box   32*32", command=lambda: boxSet(31))
    groessen_menu.add_command(label="Box   48*48", command=lambda: boxSet(47))
    groessen_menu.add_command(label="Box   64*64", command=lambda: boxSet(63))
    groessen_menu.add_command(label="Box   96*96", command=lambda: boxSet(95))
    groessen_menu.add_command(label="Box 128*128", command=lambda: boxSet(127))
    groessen_menu.add_command(label="Box 256*256", command=lambda: boxSet(255))
    groessen_menu.add_separator()
    groessen_menu.add_command(label="Muster Breite +1", command=musterXPlus1, accelerator="10er Shift /")
    groessen_menu.add_command(label="Muster Breite -1", command=musterXMinus1, accelerator="10er Shift *")
    groessen_menu.add_command(label="Muster Hoehe +1", command=musterYPlus1, accelerator="10er Shift +")
    groessen_menu.add_command(label="Muster Hoehe -1", command=musterYMinus1, accelerator="10er Shift -")
    groessen_menu.add_command(label="Muster   32*32", command=lambda: musterSet(31))
    groessen_menu.add_command(label="Muster   64*64", command=lambda: musterSet(63))
    groessen_menu.add_command(label="Muster 128*128", command=lambda: musterSet(127))
    groessen_menu.add_command(label="Muster 256*256", command=lambda: musterSet(255))
    groessen_menu.add_command(label="Muster 320*256", command=lambda: musterSet(319))

    # Untermenu Export
    export_menu = Menu(leiste)
    leiste.add_cascade(label="Export", menu=export_menu)
    export_menu.add_command(label="Muster als 'C#' Array", command=musterAlsCArray)
    export_menu.add_command(label="TLB als 'C#' Array", command=tlbAlsCArray)
    export_menu.add_command(label="Farbpalette als 'C#' Array", command=palAlsCArray)
    export_menu.add_separator()
    export_menu.add_command(label="Muster als PNG Speichern", command=lambda: musterAlsPng(False))
    export_menu.add_command(label="TLB als PNG Speichern", command=lambda: tlbAlsPng(False))
    export_menu.add_separator()
    export_menu.add_command(label="Muster als PNG Speichern Hintergrundfarbe Transparent",
                            command=musterAlsPng)
    export_menu.add_command(label="TLB als PNG Speichern Hintergrundfarbe Transparent", command=tlbAlsPng)
    export_menu.add_separator()
    export_menu.add_command(label="Muster fuer CSS base64 Image", command=musterFuerCSSBase64Image)
    export_menu.add_command(label="TLB fuer CSS base64 Image", command=tlbFuerCSSBase64Image)
    export_menu.add_separator()
    export_menu.add_command(label="TLB als ICO speichern (nur Boxgroesse)", command=tlbAlsIcoImage)
    export_menu.add_command(label="TLB als multisize ICO speichern (bis Boxgroesse)", command=tlbAlsIcoImageMul)
    export_menu.add_separator()
    export_menu.add_command(label="Muster als HTML speichern", command=musterAlsHTML)
    return


def infoTextInit():  # Lädt und stellt den Text in der Infobox zur Bedienung dar
    info_text = ScrolledText(frameInfoText, bg="#C0C0C0", width=80, height=17, font="Courier 10")
    info_text.grid(row=1, column=1)
    try:
        textfile = open('Tastaturbelegung.txt', 'r')
        for zeile in textfile:
            info_text.insert('end', zeile)
    except IOError:
        logging.error('Tastaturbelegung Info Text nicht gefunden')
    return


def palAktFarbeReDraw():  # setzt das Paletten Objekt für die Vordergrund Farbe neu
    nfarbe = "#" + format(vga_pal_rot[akt_farbe], '02x') + format(vga_pal_gruen[akt_farbe], '02x') + format(
        vga_pal_blau[akt_farbe], '02x')
    palButtonAktFarbeKachel.config(bg=nfarbe)
    pal[akt_farbe].setColor(nfarbe)
    pal[akt_farbe].drawME()
    palReglerRot.set(vga_pal_rot[akt_farbe])
    palReglerGruen.set(vga_pal_gruen[akt_farbe])
    palReglerBlau.set(vga_pal_blau[akt_farbe])
    return


def farbeReDraw():  # Malt die durch die Paletten funktionen geänderte Farbe im Teilbereich und Musterbereich neu
    tlbAktReDraw()
    musterAktReDraw()
    return


def palHinFarbeReDraw():  # setzt das Paletten Objekt für die Hintergrund Farbe neu
    nfarbe = "#" + format(vga_pal_rot[hin_farbe], '02x') + format(vga_pal_gruen[hin_farbe], '02x') + format(
        vga_pal_blau[hin_farbe], '02x')
    palButtonHinFarbeKachel.config(bg=nfarbe)
    pal[hin_farbe].setColor(nfarbe)
    pal[hin_farbe].drawME()
    return


def palFarbeTauschen():  # Reagiert auf Button im Palettenbereich Farbe Tauschen wurde geklickt, tauscht die Farben
    global akt_farbe, hin_farbe, redrawR, redrawG, redrawB
    akt_farbe, hin_farbe = hin_farbe, akt_farbe
    pal[hin_farbe].select()
    pal[hin_farbe].xcross(False)
    pal[akt_farbe].select()
    pal[akt_farbe].xcross(True)
    redrawB = False
    redrawG = False
    redrawR = False
    palAktFarbeReDraw()
    palHinFarbeReDraw()
    return


def reglerRot(wert):  # Reagiert auf die Scrollbar für Rot im Palettenbereich und Passt die Farbe an
    global vga_pal_rot, redrawR
    vga_pal_rot[akt_farbe] = int(wert)
    palLabelRotWert['text'] = format(vga_pal_rot[akt_farbe], '02x')
    palAktFarbeReDraw()
    if redrawR:
        farbeReDraw()
    redrawR = True
    return


def reglerGruen(wert):  # Reagiert auf die Scrollbar für Grün im Palettenbereich und Passt die Farbe an
    global vga_pal_gruen, redrawG
    vga_pal_gruen[akt_farbe] = int(wert)
    palLabelGruenWert['text'] = format(vga_pal_gruen[akt_farbe], '02x')
    palAktFarbeReDraw()
    if redrawG:
        farbeReDraw()
    redrawG = True
    return


def reglerBlau(wert):  # Reagiert auf die Scrollbar für Blau im Palettenbereich und Passt die Farbe an
    global vga_pal_blau, redrawB
    vga_pal_blau[akt_farbe] = int(wert)
    palLabelBlauWert['text'] = format(vga_pal_blau[akt_farbe], '02x')
    palAktFarbeReDraw()
    if redrawB:
        farbeReDraw()
    redrawB = True
    return


def reglerLupe(wert):  # Reagiert auf die Scrollbar im Lupenbereich und passt den vergrösserungs Faktor an
    global faktor
    faktor = int(wert)
    lupeDraw(1)
    return


def lupeClick(_event=None):  # Wenn auf den Lupenbereich geklickt wurde dann Lupe aktualisieren
    lupeDraw(1)
    return


def lupeDraw(malen=0):  # Malt die Lupe wenn diese auf Synchronisieren steht
    if lupeSync.get() == 1 or malen == 1:
        starteZeitmessung()
        lupeCanvas.create_rectangle(0, 0, lupe_size + faktor_max, lupe_size + faktor_max,
                                    tags='hintergrund', fill='white')
        pixel_menge = lupe_size // faktor
        malen_bis_x = mus_gx - pos_tlb_x
        malen_bis_y = mus_gy - pos_tlb_y
        if malen_bis_x > pixel_menge:
            malen_bis_x = pixel_menge
        if malen_bis_y > pixel_menge:
            malen_bis_y = pixel_menge
        for i in range(0, malen_bis_y + 1):
            for t in range(0, malen_bis_x + 1):
                k = muster_feld[pos_tlb_x + t][pos_tlb_y + i]
                nfarbe = "#" + format(vga_pal_rot[k], '02x') + format(vga_pal_gruen[k], '02x') + \
                         format(vga_pal_blau[k], '02x')
                lupeCanvas.create_rectangle(faktor * t, faktor * i, faktor * t + faktor, faktor * i + faktor,
                                            fill=nfarbe, tags="rec", width=0)
        stopZeitmessung('Lupe Draw')
    return


def sbXTlbScroll(wert):  # Reagiert auf eine Bewegung der Vertikalen Scrollbar im Teilbereich
    global in_tlb_x
    in_tlb_x = int(wert)
    tlbDraw()
    return


def sbYTlbScroll(wert):  # Reagiert auf eine Bewegung der Horizontalen Scrollbar im Teilbereich
    global in_tlb_y
    in_tlb_y = int(wert)
    tlbDraw()
    return


def starteZeitmessung():  # Startet die Zeitmessung zur ausführung einer Funktion
    global startzeit
    startzeit = time.time()
    return


def stopZeitmessung(befehl):  # Stoppt die Zeitmessung für eine Funktion und schreibt das Ergebnis in das Log
    endzeit = time.time()
    laufzeit = endzeit - startzeit
    # statusleiste["text"] = "Letzer Befehl " + str(befehl) + " dauerte :" + str(laufzeit)
    text = str(befehl) + ' duration ' + str(laufzeit) + " seconds"
    writeToLog(text)
    return


def writeToLog(text):  # Schreibt in die Logbox sowie in die Logdatei einfache INFO
    log_text.insert('end', time.strftime('%H:%M:%S') + ' ' + text + "\n")
    log_text.see(END)
    logging.info(text)
    zeilen = int(log_text.index('end-1c').split('.')[0])
    if zeilen >= 100:
        log_text.delete('1.0', '2.0')
    return


def konfig_load():  # lädt die konfigurations Datei und setzt die Einstellungen um
    global tlb_feld_size, tlb_anzahl_felder, farb_feld_size, logfile, loglevel, standardpalette
    try:
        config = open('muster.conf', 'r')
        for zeile in config:
            if zeile[0] != '#':  # Inhalt gefunden
                inhalt = zeile.split('=')
                if inhalt[0] == 'tlb_feld_size':
                    tlb_feld_size = int(inhalt[1])
                if inhalt[0] == 'tlb_anzahl_felder':
                    tlb_anzahl_felder = int(inhalt[1])
                if inhalt[0] == 'farb_feld_size':
                    farb_feld_size = int(inhalt[1])
                if inhalt[0] == 'logfile':
                    logfile = str(inhalt[1].strip())
                if inhalt[0] == 'loglevel':
                    loglevel = logtiefe[(inhalt[1].strip())]
                if inhalt[0] == 'palette':
                    standardpalette = str(inhalt[1].strip())
        config.close()
    except IOError:
        pass  # logging noch nicht initialisiert
    # writeToLog('Konfig konte nicht geladen werden')
    return


# Testfunktionen
def mausXY(event):  # Berichtet die Mausposition wenn ausserhalb definierter bereiche
    button = 0
    if event.num == 1:
        button = "1"     # Linke Maustaste
    if event.num == 2:
        button = "2"         # Mittlere Maustaste
    if event.num == 3:
        button = "3"         # Rechte Maustaste
    statusleiste["text"] = " MouseX: " + str(event.x_root) + " MouseY: " + str(event.y_root) + " Button: " + str(button)
    return


# Farbpaletten
vga_pal_rot = [0xFF, 0x00, 0xFF, 0x00, 0x00, 0xA8, 0xA8, 0xA8, 0x54, 0x54, 0x54, 0x54, 0xFF, 0xFF, 0xFF, 0xFF,
               0x00, 0x14, 0x20, 0x2C, 0x38, 0x44, 0x50, 0x60, 0x70, 0x80, 0x90, 0xA0, 0xB4, 0xC8, 0xE0, 0xFF,
               0x00, 0x40, 0x7C, 0xBC, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xBC, 0x7C, 0x40,
               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7C, 0x9C, 0xBC, 0xDC, 0xFF, 0xFF, 0xFF, 0xFF,
               0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xDC, 0xBC, 0x9C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C,
               0xB4, 0xC4, 0xD8, 0xE8, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xE8, 0xD8, 0xC4,
               0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0x00, 0x1C, 0x38, 0x54, 0x70, 0x70, 0x70, 0x70,
               0x70, 0x70, 0x70, 0x70, 0x70, 0x54, 0x38, 0x1C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
               0x38, 0x44, 0x54, 0x60, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x60, 0x54, 0x44,
               0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x50, 0x58, 0x60, 0x68, 0x70, 0x70, 0x70, 0x70,
               0x70, 0x70, 0x70, 0x70, 0x70, 0x68, 0x60, 0x58, 0x50, 0x50, 0x50, 0x50, 0x50, 0x50, 0x50, 0x50,
               0x00, 0x10, 0x20, 0x30, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x30, 0x20, 0x10,
               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x28, 0x30, 0x38, 0x40, 0x40, 0x40, 0x40,
               0x40, 0x40, 0x40, 0x40, 0x40, 0x38, 0x30, 0x28, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
               0x2C, 0x30, 0x34, 0x3C, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x3C, 0x34, 0x30,
               0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80]

vga_pal_gruen = [0xFF, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x54, 0xA8, 0x54, 0x54, 0xFF, 0xFF, 0x54, 0x54, 0xFF, 0xFF,
                 0x00, 0x14, 0x20, 0x2C, 0x38, 0x44, 0x50, 0x60, 0x70, 0x80, 0x90, 0xA0, 0xB4, 0xC8, 0xE0, 0xFF,
                 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x7C, 0xBC, 0xFF, 0xFF, 0xFF, 0xFF,
                 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xBC, 0x7C, 0x40, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C,
                 0x7C, 0x9C, 0xBC, 0xDC, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xDC, 0xBC, 0x9C,
                 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xC4, 0xD8, 0xE8, 0xFF, 0xFF, 0xFF, 0xFF,
                 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xE8, 0xD8, 0xC4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                 0x00, 0x1C, 0x38, 0x54, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x54, 0x38, 0x1C,
                 0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x44, 0x54, 0x60, 0x70, 0x70, 0x70, 0x70,
                 0x70, 0x70, 0x70, 0x70, 0x70, 0x60, 0x54, 0x44, 0x50, 0x50, 0x50, 0x50, 0x50, 0x50, 0x50, 0x50,
                 0x50, 0x58, 0x60, 0x68, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x68, 0x60, 0x58,
                 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x20, 0x30, 0x40, 0x40, 0x40, 0x40,
                 0x40, 0x40, 0x40, 0x40, 0x40, 0x30, 0x20, 0x10, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
                 0x20, 0x28, 0x30, 0x38, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x38, 0x30, 0x28,
                 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x30, 0x34, 0x3C, 0x40, 0x40, 0x40, 0x40,
                 0x40, 0x40, 0x40, 0x40, 0x40, 0x3C, 0x34, 0x30, 0x00, 0x00, 0x00, 0xFF, 0x80, 0xFF, 0x80, 0x00]

vga_pal_blau = [0xFF, 0x00, 0x00, 0x00, 0xFF, 0xA8, 0x00, 0xA8, 0x54, 0xFF, 0x54, 0xFF, 0x54, 0xFF, 0x54, 0xFF,
                0x00, 0x14, 0x20, 0x2C, 0x38, 0x44, 0x50, 0x60, 0x70, 0x80, 0x90, 0xA0, 0xB4, 0xC8, 0xE0, 0xFF,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xBC, 0x7C, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x40, 0x7C, 0xBC, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xDC, 0xBC, 0x9C,
                0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x7C, 0x9C, 0xBC, 0xDC, 0xFF, 0xFF, 0xFF, 0xFF,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xE8, 0xD8, 0xC4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4, 0xB4,
                0xB4, 0xC4, 0xD8, 0xE8, 0xFF, 0xFF, 0xFF, 0xFF, 0x70, 0x70, 0x70, 0x70, 0x70, 0x54, 0x38, 0x1C,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1C, 0x38, 0x54, 0x70, 0x70, 0x70, 0x70,
                0x70, 0x70, 0x70, 0x70, 0x70, 0x60, 0x54, 0x44, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38,
                0x38, 0x44, 0x54, 0x60, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x68, 0x60, 0x58,
                0x50, 0x50, 0x50, 0x50, 0x50, 0x50, 0x50, 0x50, 0x50, 0x58, 0x60, 0x68, 0x70, 0x70, 0x70, 0x70,
                0x40, 0x40, 0x40, 0x40, 0x40, 0x30, 0x20, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x10, 0x20, 0x30, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x38, 0x30, 0x28,
                0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x28, 0x30, 0x38, 0x40, 0x40, 0x40, 0x40,
                0x40, 0x40, 0x40, 0x40, 0x40, 0x3C, 0x34, 0x30, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C, 0x2C,
                0x2C, 0x30, 0x34, 0x3C, 0x40, 0x40, 0x40, 0x40, 0x00, 0xFF, 0xA0, 0x00, 0x00, 0xFF, 0x80, 0x80]

# Globale Werte festlegen
mus_gx_max = 320  # Maximalgröße des Musters festlegen
mus_gy_max = 256
startzeit = 0   # Für Zeitmesser Funktion

# Muster Feld definieren und anlegen
muster_feld = [[0 for y in range(mus_gy_max + 1)] for x in range(mus_gx_max + 1)]

# weitere Variablen initialisieren
mus_gx = 319  # Veränderbare Größe des Musters initalwert
mus_gy = 255
pos_tlb_x = 0  # Position des Teilbereich innerhalb des Musters
pos_tlb_y = 0
pos_tlb_x_merken = 0    # Merker für Kopierbefehl
pos_tlb_y_merken = 0
kopieren = False    # Status ob Kopiewren gedrückt wurde
in_tlb_x = 0    # Bei Scrollen in der edit Fläche merken wo wir sind
in_tlb_y = 0
tlb_size = 31   # Bestimmt die Anzahl der Klickbaren Felder in x und y
tlb_anzahl_felder = 32  # Felder pro Achse
tlb_feld_size = 20  # Bestimmte die Pixel Größe des feldes in breite und höhe

# farb_feld_begin_x = 1  # bestimmt die Postion der Farbpalette innerhalb des Panels
# farb_feld_begin_y = 1
farb_feld_size = 30  # Bestimmt die Größe des Palettenfeld
akt_farbe = 1  # Aktueller Paletten eintrag zum malen
hin_farbe = 0  # Paletten eintrag der genutzt wird zum löschen
sb_x_tlb_value = 0  # Scrollbar Teilbereich Position
sb_x_tlb_maximum = 0
sb_y_tlb_value = 0
sb_y_tlb_maximum = 0
pos_bm_x = 5  # Position des Canvas im Frame
pos_bm_y = 5
faktor = 2  # Initialwert für Lupenfaktor
faktor_max = 60  # Begrenzung der Maximalen Lupenvergrößerung
lupe_size = 400  # Breite und Höhe für Lupen Canvas
drag_the_box = False  # Wird die Box bewegt
box_max = 256   # maximale Box Größe
box_min = 16    # minimale Boxgröße
button1pressed = False  # Button Status
button2pressed = False
button3pressed = False
redrawR = True  # Farb Redraw nicht bei Palettenklick
redrawG = True
redrawB = True
standardpalette = ''  # benutze interne Palette
logtiefe = {'NOTSET': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
logfile = 'musterEditor.log'
loglevel = 0  # NOTSET


# Umgebungsvariablen gesetz Konfigurationsdatei laden und umsetzen
konfig_load()
# Konfigurationabhänge Variablen setzten
tlb_rec_size = tlb_feld_size-1  # Bestimmt die Größe des Klickbaren Rechtecks

# Logging Init
logging.getLogger('MusterEditor')
logging.basicConfig(filename=logfile, level=loglevel,
                    format="{asctime} [{levelname}] {message}",
                    datefmt="%Y.%m.%d %H:%M:%S", style="{")
logging.info('Muster Editor gestartet')
logging.critical('No Critical INFO LOGLEVEL='+str(loglevel))

# Prüfe ob Standard Palette durch Konfig Datei gesetzt wurde dann laden
if len(standardpalette):
    logging.info('Es wurde eine neue Palette vorgegeben')
    palLoad(standardpalette)


# Größen der Widgets die eine Angabe benötigen
frameTeilbereich_breite = tlb_feld_size * (tlb_anzahl_felder + 4)
frameTeilbereich_hoehe = tlb_feld_size * (tlb_anzahl_felder + 4)

frameMuster_breite = mus_gx_max + pos_bm_x + 20
frameMuster_hoehe = mus_gy_max + 45

# Definere Hauptfenster
hauptfenster = Tk()
hauptfenster.title("Muster Editor V1.0")
menueInit()  # Menue zum Hauptfenster

# innerframe defineren
posFrameTlb = Frame(hauptfenster)
posFrameMusTxt = Frame(hauptfenster)
posFramePalLup = Frame(hauptfenster)

# Frames definieren
frameTeilbereich = LabelFrame(posFrameTlb, width=frameTeilbereich_breite, height=frameTeilbereich_hoehe,
                              text="Teilbereich")
frameLogging = LabelFrame(hauptfenster, text="Logging")
frameMuster = LabelFrame(posFrameMusTxt, width=frameMuster_breite, height=frameMuster_hoehe, text="Muster")
frameInfoText = LabelFrame(posFrameMusTxt, text="Tastaturbelegung")
framePalette = LabelFrame(posFramePalLup, text="Farbpalette")
frameLupe = LabelFrame(posFramePalLup, text="Lupe")

posFrameTlb.grid(row=1, column=1, rowspan=2, sticky='nw')
posFrameMusTxt.grid(row=1, column=2, sticky='nw')
posFramePalLup.grid(row=2, column=2, sticky='nw')

frameTeilbereich.grid(row=1, column=1, sticky='NW')
frameLogging.grid(row=3, column=1, columnspan=2, sticky='NW')
frameMuster.grid(row=1, column=1, sticky='NW')
frameInfoText.grid(row=1, column=2, sticky='NW')
framePalette.grid(row=1, column=1, sticky='NW')
frameLupe.grid(row=1, column=2, sticky='NE')

# Statusleiste am unteren Rand
statusleiste = Label(hauptfenster, text="", anchor="w")
statusleiste.grid(row=4, column=1, columnspan=2, sticky='NW')

# Loggingausgabe Feld
log_text = ScrolledText(frameLogging, bg="#f0f0f0", width=80, height=4, font="Courier 10")
log_text.grid(row=1, column=1)

# Canvas Muster definieren
musterCanvas = Canvas(frameMuster, width=mus_gx_max+10, height=mus_gy_max+10, bg="#FFFFFF")
musterCanvas.place(x=pos_bm_x, y=pos_bm_y)
musterImg = PhotoImage(width=mus_gx_max, height=mus_gy_max)
musterImage = musterCanvas.create_image((mus_gx_max / 2) + 5, (mus_gy_max / 2) + 5, image=musterImg, state="normal",
                                        tags="bild")
musterCanvas.bind("<ButtonPress-1>", musterCanvasMouseDown)
musterCanvas.bind("<ButtonPress-3>", musterCanvasMouseDown)
musterCanvas.bind("<ButtonRelease-1>", musterCanvasMouseUp)
musterCanvas.bind("<ButtonRelease-3>", musterCanvasMouseUp)
musterCanvas.bind("<Motion>", musterCanvasMouseMove)

dragBox = musterCanvas.create_rectangle(pos_bm_x + pos_tlb_x - 1, pos_bm_y + pos_tlb_y - 1,
                                        pos_bm_x + pos_tlb_x - 1 + tlb_size + 4,
                                        pos_bm_y + pos_tlb_y - 1 + tlb_size + 4,
                                        bg=None, width=3, tags="dragbox", activeoutline='#FFFFFF',
                                        disabledoutline='#F0F0F0')
# Canvas tlb definieren
teilbereichCanvas = Canvas(frameTeilbereich, width=(tlb_size + 1) * tlb_feld_size,
                           height=(tlb_size + 1) * tlb_feld_size, bg="#FFFFFF")
teilbereichCanvas.place(x=5, y=1)
teilbereichCanvas.bind("<ButtonPress-1>", tlbCanvasMouseDown)
teilbereichCanvas.bind("<ButtonPress-2>", tlbCanvasMouseDown)
teilbereichCanvas.bind("<ButtonPress-3>", tlbCanvasMouseDown)
teilbereichCanvas.bind("<ButtonRelease-1>", tlbCanvasMouseUp)
teilbereichCanvas.bind("<ButtonRelease-2>", tlbCanvasMouseUp)
teilbereichCanvas.bind("<ButtonRelease-3>", tlbCanvasMouseUp)
teilbereichCanvas.bind("<Motion>", tlbCanvasMouseMove)
tlbReglerX = Scale(frameTeilbereich, from_=sb_x_tlb_value, to=sb_x_tlb_maximum, orient=HORIZONTAL, showvalue=0,
                   length=tlb_feld_size * tlb_anzahl_felder, width=15, command=sbXTlbScroll,
                   sliderlength=tlb_feld_size * tlb_anzahl_felder)
tlbReglerY = Scale(frameTeilbereich, from_=sb_y_tlb_value, to=sb_y_tlb_maximum, orient=VERTICAL, showvalue=0,
                   length=tlb_feld_size * tlb_anzahl_felder, width=15, command=sbYTlbScroll,
                   sliderlength=tlb_feld_size * tlb_anzahl_felder)
tlbReglerX.place(x=1, y=frameTeilbereich_breite - 45)
tlbReglerY.place(y=1, x=frameTeilbereich_hoehe - 35)

# Canvas farbpalette definieren
palCanvas = Canvas(framePalette, width=16 * farb_feld_size+1, height=16 * farb_feld_size+1, bg="#ffffff")
palCanvas.grid(row=1, column=1, rowspan=8, sticky='nw')

palCanvas.bind("<Button-1>", palCanvasMouse)
palCanvas.bind("<Button-3>", palCanvasMouse)
palCanvas.bind("<Motion>", palCanvasMouse)

# Pixel Bitmap für Labelgrösse um Label in pixel zu defineren (kleiner Trick)
pixelGrafik = PhotoImage(width=1, height=1)
# Label für Text Aktuelle Farbe
palLabelAktFarbe = Label(framePalette, text='Aktuelle Farbe')
palLabelAktFarbe.grid(row=1, column=3, columnspan=3)
# Farbkachel für Aktuelle Farbe
farbe = "#" + format(vga_pal_rot[akt_farbe], '02x') + format(vga_pal_gruen[akt_farbe], '02x') + format(
    vga_pal_blau[akt_farbe], '02x')
palButtonAktFarbeKachel = Label(framePalette, bg=farbe, width=farb_feld_size*6,
                                height=farb_feld_size, image=pixelGrafik)
palButtonAktFarbeKachel.grid(row=2, column=3, columnspan=3)
# Ausgabe Farbwerte in Hex
palLabelRotWert = Label(framePalette, text=format(vga_pal_rot[akt_farbe], '02x'))
palLabelGruenWert = Label(framePalette, text=format(vga_pal_gruen[akt_farbe], '02x'))
palLabelBlauWert = Label(framePalette, text=format(vga_pal_blau[akt_farbe], '02x'))
palLabelRotWert.grid(row=3, column=3)
palLabelGruenWert.grid(row=3, column=4)
palLabelBlauWert.grid(row=3, column=5)
# R G B als Text schreiben
palLabelRot = Label(framePalette, text="R", bg='#FF0000')
palLabelGruen = Label(framePalette, text="G", bg='#00FF00')
palLabelBlau = Label(framePalette, text="B", bg='#0000FF')
palLabelRot.grid(row=4, column=3)
palLabelGruen.grid(row=4, column=4)
palLabelBlau.grid(row=4, column=5)
# Regler für Palette
palReglerRot = Scale(framePalette, from_=255, to=0, orient=VERTICAL, showvalue=1,
                     length=farb_feld_size*8, width=15, command=reglerRot)
palReglerGruen = Scale(framePalette, from_=255, to=0, orient=VERTICAL, showvalue=1,
                       length=farb_feld_size*8, width=15, command=reglerGruen)
palReglerBlau = Scale(framePalette, from_=255, to=0, orient=VERTICAL, showvalue=1,
                      length=farb_feld_size*8, width=15, command=reglerBlau)
palReglerRot.grid(row=5, column=3)
palReglerGruen.grid(row=5, column=4)
palReglerBlau.grid(row=5, column=5)

farbe = "#" + format(vga_pal_rot[hin_farbe], '02x') + format(vga_pal_gruen[hin_farbe], '02x') + format(
    vga_pal_blau[hin_farbe], '02x')
palButtonFarbeTausche = Button(framePalette, text="Tauschen", command=palFarbeTauschen)
palButtonFarbeTausche.grid(row=6, column=3, columnspan=3)
# Label für Text Hintergrundfarbe
palLabelHinFarbe = Label(framePalette, text='Hintergund Farbe')
palLabelHinFarbe.grid(row=7, column=3, columnspan=3)
# Label alsa Farbkachel für Hintergrundfarbe
palButtonHinFarbeKachel = Label(framePalette, bg='#FFFFFF', width=farb_feld_size*6,
                                height=farb_feld_size, image=pixelGrafik)
palButtonHinFarbeKachel.grid(row=8, column=3, columnspan=3)

# Canvas Lupe definieren
lupeCanvas = Canvas(frameLupe, width=farb_feld_size*13, height=farb_feld_size*14)
lupeRegler = Scale(frameLupe, from_=2, to=faktor_max, orient=HORIZONTAL, showvalue=1,
                   length=farb_feld_size*13, width=15, command=reglerLupe)
lupeSync = IntVar()  # Lupe ständig mit Synchronisieren?
lupeSyncCheck = Checkbutton(frameLupe, text="Lupe Sync", variable=lupeSync)

lupeCanvas.grid(row=1, column=1)
lupeRegler.grid(row=2, column=1)
lupeSyncCheck.grid(row=3, column=1)
lupeCanvas.bind("<Button-1>", lupeClick)

# Array für Palettenfarben erstellen
pal = [PalRec(palCanvas, "Fx0y0")]  # Array für palette
palInit()  # Malt die Palette und ergänzt um Objekte

# Array für Teilbereich erstellen
tlb = [TlbRec(teilbereichCanvas, "Tx0y0")]  # Später Array für tlb
tlbInit()  # malt den Tlb initial und ergänzt um Objekte

# Info Text zur Tastaturbelegung laden
infoTextInit()

# Tasten binden auf das Hauptfenster
hauptfenster.bind("<Key>", tasten)
# hauptfenster.bind("<Motion>", mausXY)
hauptfenster.protocol("WM_DELETE_WINDOW", programmBeenden)
hauptfenster.mainloop()
