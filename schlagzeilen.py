import feedparser
import spacy
from random import choice
from configparser import ConfigParser
try:
    from feedspezifika import *
except ImportError:
    pass


class ZwoaSchlogzeiln():
    def cleanup(self, titel):
        chars = ['„', '“', '”']
        for char in chars:
            titel = titel.replace(char, '')
        return titel

    def __init__(self):
        # Globale Variablen
        self.titel = []
        self.kurzetitel = []
        self.subj = []

        # Konfiguration laden
        cfg = ConfigParser()
        cfg.read('zwoaschlogzeiln.ini')

        # Konfigurierte Sources parsen
        for name, url in cfg.items('sources'):
            feed = feedparser.parse(url)
            
            # Feedspezifische Filter anwenden, d.h. feedspezifika.<feedname>() aufrufen (sofern existent)
            for entry in feed.entries:
                try:
                    entry = globals()[name](entry)
                except KeyError:
                    # entry unverändert lassen
                    pass
                if entry:   # Weitermachen, falls der Entry noch existiert und nicht weggefiltert (=auf None gesetzt) wurde
                    if entry['title'].count(' ') > 1:
                        self.titel.append(self.cleanup(entry['title']))
                    else:
                        self.kurzetitel.append(self.cleanup(entry['title']))

        # SpaCy initialisieren
        self.nlp = spacy.load('de')

        # Sämtliche Titel durch SpaCy jagen und eine Liste aller Nomen und Eigennamen erstellen
        for titel in (self.titel + self.kurzetitel):	# für den Korpus sind die kurzen Titel gut genug
            titel = self.nlp(titel)
            tsubj = [str(k) for k in titel if k.pos_ in ('PROPN', 'NOUN')]
            self.subj = self.subj + tsubj


    def schlagzeile_generieren(self):
        # Zufällige Schlagzeile wählen und nochmals durch SpaCy jagen
        satz = choice(self.titel)
        satz = self.nlp(satz)

        # Von der ausgewählten Schlagzeile ebenfalls alle Nomen und Eigennamen extrahieren
        satzsubj = [str(k) for k in satz if k.pos_ in ('PROPN', 'NOUN')]
        
        # Alle Wörter in eine neue Liste kopieren
        satzneu = []
        satzneu = ' '.join([str(k) for k in satz])
        
        # Zufällig einen Nomen/Eigennamen auswählen, der ersetzt werden soll
        wortalt = choice(satzsubj)
        
        # Ausgewähltes Wort aus der Wortliste streichen
        self.subj.remove(wortalt)

        # Zufällig einen Nomen/Eigennamen auswählen aus der Liste aller Nomen/Eigennamen...
        wortneu = choice(self.subj)

        # ... und ersetzen
        satzneu = satzneu.replace(str(wortalt), str(wortneu))

        # Punktuation bereinigen
        satzneu = satzneu.replace(' : ', ': ')
        satzneu = satzneu.replace(' . ', '. ')
        satzneu = satzneu.replace(' ?', '?')
        satzneu = satzneu.replace(' .', '.')
        satzneu = satzneu.replace(' !', '!')

        # Fertig!
        return satzneu