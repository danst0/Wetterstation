#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import time, datetime
import copy

class Graphs:
    font = {
        'family' : 'sans-serif',
        'weight' : 'ultralight',
        'size'   : 9}
    def __init__(self, datenbank, full_base_path):
        self.d = datenbank
        self.full_base_path = full_base_path

        
    def aggregate_data(self, daten, dauer):
#         updatefrequenz: 3 min -> 20 Werte pro Stunde
#         60 min -> nicht (20 Werte)
#         24h -> 30 min (48)
#         1 Woche -> 3h (56)
#         1 Monat -> 12 h (60)
#         1 Quartal -> 48 h (45)
#         1 Jahr -> 6 Tage (60)
#         Alles -> ?
        if daten == []:
            return []
        neue_daten = []
#         print dauer
        if dauer.startswith('1 Stunde'):
            neue_daten = copy.deepcopy(daten)
        elif dauer.startswith('24 Stunden'):
            first_point = datetime.datetime.now()
#             print first_point
            halbe_stunde = int(round((first_point.minute)/60.0*2, 0)/2.0*60)
            zusatz = 0
            if halbe_stunde == 60:
                halbe_stunde = 0
                zusatz = 1
            first_point = first_point.replace(minute=halbe_stunde, second=0, microsecond=0)
            first_point = first_point + datetime.timedelta(hours=zusatz)
#             print first_point
            times = []
            for i in range(48):
                times.append(first_point - datetime.timedelta(minutes=30*i))
#             pprint(times)
#             sys.exit()
            for time in times:
                counter = 0
                i = 0
                average = 0
                while i < len(daten):
                    datum = daten[i]
                    if datum[0] >= time - datetime.timedelta(minutes=15) and datum[0] < time + datetime.timedelta(minutes=15):
                        del daten[i]
                        counter += 1
                        average += datum[3]
                    i += 1
                if counter > 0:
                    average = average/float(counter)
                neue_daten.append((time, daten[0][1], daten[0][2], average))
        elif dauer.startswith('7 Tage'):
            first_point = datetime.datetime.now()
            drei_stunden = int(round((first_point.hour)/24.0*8, 0)/8.0*24)
            zusatz = 0
            if drei_stunden == 24:
                drei_stunden = 0
                zusatz = 1
            first_point = first_point.replace(hour=drei_stunden, minute=0, second=0, microsecond=0)
            first_point = first_point + datetime.timedelta(days=zusatz)
            times = []
            for i in range(56):
                times.append(first_point - datetime.timedelta(hours=3*i))
            for time in times:
                counter = 0
                i = 0
                average = 0
                while i < len(daten):
                    datum = daten[i]
                    if datum[0] >= time - datetime.timedelta(hours=1.5) and datum[0] < time + datetime.timedelta(hours=1.5):
                        del daten[i]
                        counter += 1
                        average += datum[3]
                    i += 1
                if counter > 0:
                    average = average/float(counter)
                neue_daten.append((time, daten[0][1], daten[0][2], average))
        elif dauer.startswith('30 Tage'):
            first_point = datetime.datetime.now()
#             print first_point
            zwoelf_stunden = int(round((first_point.hour)/24.0*2, 0)/2.0*24)
            if zwoelf_stunden == 24:
                zwoelf_stunden = 0
            first_point = first_point.replace(hour=zwoelf_stunden, minute=0, second=0, microsecond=0)
#             print first_point
            times = []
            for i in range(60):
                times.append(first_point - datetime.timedelta(hours=12*i))
#             pprint(times)
#             sys.exit()
            for time in times:
                counter = 0
                i = 0
                average = 0
                while i < len(daten):
                    datum = daten[i]
                    if datum[0] >= time - datetime.timedelta(hours=6) and datum[0] < time + datetime.timedelta(hours=6):
                        del daten[i]
                        counter += 1
                        average += datum[3]
                    i += 1
                if counter > 0:
                    average = average/float(counter)
                neue_daten.append((time, daten[0][1], daten[0][2], average))
        elif dauer.startswith('1 Quartal'):
            first_point = datetime.datetime.now()
#             print first_point
            stunden = int(round((first_point.hour)/24.0/2, 0)*2.0*24)
            first_point = first_point.replace(hour=stunden, minute=0, second=0, microsecond=0)
#             print first_point
            times = []
            for i in range(45):
                times.append(first_point - datetime.timedelta(hours=12*i))
#             pprint(times)
#             sys.exit()
            for time in times:
                counter = 0
                i = 0
                average = 0
                while i < len(daten):
                    datum = daten[i]
                    if datum[0] >= time - datetime.timedelta(hours=24) and datum[0] < time + datetime.timedelta(hours=24):
                        del daten[i]
                        counter += 1
                        average += datum[3]
                    i += 1
                if counter > 0:
                    average = average/float(counter)
                neue_daten.append((time, daten[0][1], daten[0][2], average))

        elif dauer.startswith('1 Jahr'):
            first_point = datetime.datetime.now()
            tag = int(round((first_point.day)/360.0*60, 0)/60.0*360)
            first_point = first_point.replace(day=tag, hour=0, minute=0, second=0, microsecond=0)
            times = []
            for i in range(60):
                times.append(first_point - datetime.timedelta(days=6*i))
            for time in times:
                counter = 0
                i = 0
                average = 0
                while i < len(daten):
                    datum = daten[i]
                    if datum[0] >= time - datetime.timedelta(days=3) and datum[0] < time + datetime.timedelta(days=3):
                        del daten[i]
                        counter += 1
                        average += datum[3]
                    i += 1
                if counter > 0:
                    average = average/float(counter)
                neue_daten.append((time, daten[0][1], daten[0][2], average))
        elif dauer.startswith('Alles'):
            first_point = datetime.datetime.now()
            first_point = first_point.replace(month=first_point.month, day=1, hour=0, minute=0, second=0, microsecond=0)
#             print first_point
            times = []
            for i in range(40):
                times.append(first_point - datetime.timedelta(days=30*i))
#             pprint(times)
#             sys.exit()
            for time in times:
                counter = 0
                i = 0
                average = 0
                while i < len(daten):
                    datum = daten[i]
                    if datum[0] >= time - datetime.timedelta(days=15) and datum[0] < time + datetime.timedelta(days=15):
                        del daten[i]
                        counter += 1
                        average += datum[3]
                    i += 1
                if counter > 0:
                    average = average/float(counter)
                neue_daten.append((time, daten[0][1], daten[0][2], average))


        else:
            print dauer
            neue_daten = copy.deepcopy(daten)            

                
              
#             pprint (neue_daten)

#             print viertel_stunde
            
#             sys.exit()
        return neue_daten

    def aggregate_graph(self, von, bis, raeume, arten, basename, date_format_string, groesse=(8,4), hd=False): 
        if hd:
            details=200
            basename = basename + '_hd'
            self.font['size'] = 9
        else:
            details=200
            self.font['size'] = 9
        matplotlib.rc('font', **self.font)
        fig = plt.figure(figsize=groesse, dpi=details)
        ax = fig.add_subplot(111)
        # War mal '%Y-%m-%d %H:%M:%S'
        ax.xaxis_date()
        xfmt = md.DateFormatter(date_format_string)
        ax.xaxis.set_major_formatter(xfmt)
        fig.autofmt_xdate()
        plt.xlabel('Datum/Uhrzeit')
        plt.grid(True)
        loc = matplotlib.dates.AutoDateLocator()
#         print 'loc', basename
        if basename.startswith('1 Stunde'):
#             print range(0,5,5)
            loc = matplotlib.dates.MinuteLocator(byminute=range(0,60,5))
        elif basename.startswith('24 Stunden'):
            if groesse == (7,2):
                loc = matplotlib.dates.HourLocator(interval=2)
            else:
                loc = matplotlib.dates.HourLocator(interval=4)
            
        elif basename.startswith('24 Stunden'):
            loc = matplotlib.dates.HourLocator()
        elif basename.startswith('7 Tage'):
            loc = matplotlib.dates.DayLocator()
#         elif basename.startswith('30 Tage'):
#             loc = matplotlib.dates.WeekdayLocator(byweekday=(matplotlib.dates.SA, matplotlib.dates.SU, matplotlib.dates.TU, matplotlib.dates.TH))
#         elif basename.startswith('1 Quartal'):
#             loc = matplotlib.dates.DayLocator(interval=5)
#         elif basename.startswith('1 Jahr'):
#             loc = matplotlib.dates.WeekdayLocator(byweekday=(matplotlib.dates.SA, matplotlib.dates.SU, matplotlib.dates.TU, matplotlib.dates.TH))
#         elif basename.startswith('Alles'):
#             loc = matplotlib.dates.WeekdayLocator(byweekday=(matplotlib.dates.SA, matplotlib.dates.SU, matplotlib.dates.TU, matplotlib.dates.TH))

        ax.xaxis.set_major_locator(loc)
        for raum in raeume:
            for art in arten:
             
                plt.ylabel(art)
                daten = self.d.choose(von, bis, raum, art)
                aggregat = self.aggregate_data(daten['roh'], basename)
                list_of_datetimes = map(lambda x: x[0], aggregat)
                datum = matplotlib.dates.date2num(list_of_datetimes)   
                inhalt = map(lambda x: x[3], aggregat)
                if inhalt != []:
                    plt.plot(datum, inhalt, label=raum, marker='.')
        if hd:
            plt.legend(loc='best')
            fig.suptitle(u'Verlauf zwischen ' + str(von) + ' und ' + str(bis), fontsize=8)
        else:
            plt.legend(loc='upper left')
        pfad = self.full_base_path + 'html/diagramme/' + u'Räume' + '_' + ''.join(arten) + '_' + basename + '.png'
#         print pfad
        fig.savefig(pfad)
        plt.close()
        
    def base_graph(self, von, bis, raum, art, basename, date_format_string):
        self.font['size'] = 9
        matplotlib.rc('font', **self.font)
        daten = self.d.choose(von, bis, raum, art)
        if daten['roh'] != []:
#             pprint(daten)
            list_of_datetimes = map(lambda x: x[0], daten['roh'])
            datum = matplotlib.dates.date2num(list_of_datetimes)
        
            inhalt = map(lambda x: x[3], daten['roh'])

            fig = plt.figure()
            ax = fig.add_subplot(111)
            # War mal '%Y-%m-%d %H:%M:%S'
            xfmt = md.DateFormatter(date_format_string)
            ax.xaxis.set_major_formatter(xfmt)
            fig.autofmt_xdate()
            ax.plot(datum, inhalt)
            plt.show()
#             print 'Speichere: ' + 'html/diagramme/' + raum + '_' + art + '_' + basename + '.png'
#             fig.savefig(self.full_base_path + 'html/diagramme/' + raum + '_' + art + '_' + basename + '.png')
            plt.close()

    def generate_graphs(self):
#         print d.get_distinct_art()
        nur_datum = '%d.%m.%y'
        datum_tag = '%a, %d.'
        print 'Generiere Diagramme'
        for art in self.d.get_distinct_art():
            print art
            for raum in self.d.get_distinct_raum():
                self.base_graph(datetime.datetime.now() - datetime.timedelta(hours=1), datetime.datetime.now(), raum, art, '1 Stunde', '%H:%M')     
                self.base_graph(datetime.datetime.now() - datetime.timedelta(hours=24), datetime.datetime.now(), raum, art, '24 Stunden', '%H:%M')
            size = (7,3)
            if art in ['Licht', 'Feuchtigkeit']:
                size = (3,3)
            
            for details in [True, False]:
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(hours=1), datetime.datetime.now(), self.d.get_distinct_raum(), (art,), '1 Stunde', '%H:%M', groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(hours=24), datetime.datetime.now(), self.d.get_distinct_raum(), (art,), '24 Stunden', '%H:%M', groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=7), datetime.datetime.now(), self.d.get_distinct_raum(), (art,), '7 Tage', datum_tag, groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now(), self.d.get_distinct_raum(), (art,), '30 Tage', nur_datum, groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now(), self.d.get_distinct_raum(), (art,), '1 Quartal', nur_datum, groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now(), self.d.get_distinct_raum(), (art,), '1 Jahr', nur_datum, groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=11365), datetime.datetime.now(), self.d.get_distinct_raum(), (art,), 'Alles', nur_datum, groesse=size, hd=details)
            
        