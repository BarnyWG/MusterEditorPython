# Klassen für Mustereditor


# Static Method
def _saveFarbwert(farbe):
    if farbe > 255:
        return 255
    if farbe < 0:
        return 0
    return farbe


class TlbRec:
    """
    TlbRec Grundklasse für den Teilbereich

    Bei Aufruf ist das Zielcanvas und der zu verwendende Tag zu übergeben.
    Der Tag verhindert eine endlose Zahl von Grafikobjekten, die schließlich den Speicher überfordern würden.

    Funktionen:

    setColorRGB(Rotwert,Gruenwert,Blauwert)
    setzt die Füllfarbe des Rechtecks mit den RGB Werten.

    setColor(Farbe)
    nimmt die Füllfarbe in form von HTML üblichen Farbwerten entgegen z.B #F0123d

    drawMe()
    zeichnet das element neu

    setTag(tag)
    ermöglicht es dem TlbRec ein neues Tag zuzuweisen

    setPosX(X)
    setzt die Zeichenposition auf der X-Achse

    setPosY(Y)
    setzt die Zeichenposition auf der Y-Achse

    setSize(pixel)
    setzen der größe des TlbRec in höhe und breite
    """
    _saveFarbwert = staticmethod(_saveFarbwert)

    def __init__(self, ziel, tag):
        self.pos_x = 0
        self.pos_y = 0
        self.size = 20
        self.r = 255
        self.g = 0
        self.b = 255
        self.ziel = ziel
        self.tag = tag
        return

    def setColorRGB(self, r, g, b):
        """

        :param r: Farbwert Rot
        :param g: Farbwert Grün
        :param b: Farbewert Blau
        :return: Keine Rückgabe
        """
        self.r = self._saveFarbwert(r)
        self.g = self._saveFarbwert(g)
        self.b = self._saveFarbwert(b)
        return

    def setColor(self, farbe):  # Hexcode übergabe #FE5431
        """

        :param farbe: HTML Farbcode z.B. #FEFEC0
        :return: Keine Rückgabe
        """
        self.r = int(farbe[1:3], 16)
        self.g = int(farbe[3:5], 16)
        self.b = int(farbe[5:], 16)
        return

    def drawME(self):
        farbe = "#"+format(self.r, '02x')+format(self.g, '02x')+format(self.b, '02x')
        self.ziel.create_rectangle(self.pos_x, self.pos_y, self.pos_x + self.size, self.pos_y + self.size,
                                   fill=farbe, tags=self.tag, width=0)
        return

    def setTag(self, tag):
        self.tag = tag
        return

    def setPosX(self, x):
        self.pos_x = x
        return

    def setPosY(self, y):
        self.pos_y = y
        return

    def setSize(self, size):
        self.size = size
        return


class PalRec(TlbRec):
    """
    PalRec
    für Grundfunktionen siehe TlbRec

    erweiterung der Klasse TlbRec

    Funktionen:
    select()
    bedingt das zeichnen eines 2 Farbigen Kreuzes auf dem Element beim nächsten aufruf von DrawMe()

    unselect()
    es wird kein Kreuz gezeichnet, anfangsbedingung.

    xcross(boolean)
    bestimmt die Form des Kreuzes X oder christlich
    """
    def __init__(self, ziel, tag):
        TlbRec.__init__(self, ziel, tag)
        self.selected = False
        self.crossed = False
        return

    def select(self):
        self.selected = True
        return

    def unselect(self):
        self.selected = False
        return

    def drawME(self):
        farbe = "#" + format(self.r, '02x') + format(self.g, '02x') + format(self.b, '02x')
        self.ziel.create_rectangle(self.pos_x, self.pos_y, self.pos_x + self.size, self.pos_y + self.size,
                                   fill=farbe, tags=self.tag, width=1)
        if self.selected and self.crossed:
            self.ziel.create_line(self.pos_x, self.pos_y, self.pos_x + self.size,
                                  self.pos_y + self.size, fill="black", width=3)
            self.ziel.create_line(self.pos_x + self.size, self.pos_y, self.pos_x,
                                  self.pos_y + self.size, fill="white", width=3)
        elif self.selected and self.crossed is False:
            self.ziel.create_line(self.pos_x + (self.size/2), self.pos_y, self.pos_x
                                  + (self.size/2), self.pos_y + self.size, fill="black", width=3)
            self.ziel.create_line(self.pos_x, self.pos_y + (self.size/2), self.pos_x
                                  + self.size, self.pos_y + (self.size / 2), fill="white", width=3)
        return

    def xcross(self, xbool):
        """
        :param xbool: True setzt das X False das Christliche Kreuz
        :type xbool: bool
        """
        self.crossed = xbool
        return
