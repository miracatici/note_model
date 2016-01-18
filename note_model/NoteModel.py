# -*- coding: utf-8 -*-

import json
import os
from tonic_identifier.PitchDistribution import hz_to_cent
from tonic_identifier.tonic_identifier import TonicLastNote
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker

class NoteModel:
    def __init__(self):
        pass

    @staticmethod
    def calculate_notes(distribution, tonichz, makam):
        '''
        Identify the names of performed notes from histogram peaks (stable pitches).
        '''

        # Reading dictionary which contains note symbol, theoretical names and their cent values
        note_file = os.path.join(os.path.dirname(os.path.abspath("note_dict.json")),
                                 'note_model/data', 'note_dict.json')           #os-independet path
        note_dict = json.load(open(note_file, 'r'))

        # Reading dictionary which contains theoretical information about each makam
        makam_file = os.path.join(os.path.dirname(os.path.abspath("makam_extended.json")),
                                 'note_model/data', 'makam_extended.json')      #os-independet path
        makam_extended = json.load(open(makam_file, 'r'))

        # Reading value from note_dict.json file
        teoNoteCent = {}                               # A dictionary for theoretical cent values of notes
        for key in note_dict.keys():
            teoNoteCent[key] = (int(note_dict[key]["Value"]))

        # Defining tonic (karar) symbol from theoretical information
        note_symbol = makam_extended[makam]["karar_symbol"]

        # Conversion hertz to cent, both of performed and theoretical values
        c0 = 16.35                                                             # Reference is C0, unit is Hz
        tonic_cent = hz_to_cent(tonichz, c0)[0]
        teoretical_cent = teoNoteCent[note_symbol]

        # Normalize ratio which is between theory and performance
        ratio = teoretical_cent / tonic_cent

        # Calculate stable pitches
        peaks = distribution.detect_peaks()
        peakId = peaks[0]
        stable_pitches = distribution.bins[peakId]
        stable_pitches_cent = hz_to_cent(stable_pitches, c0)
        stable_pitches_cent_norm = stable_pitches_cent * ratio

        # Finding nearest theoretical values of each stable pitch, identify the name of this value and write to output
        performedNotes = {}                            # Defining output (return) object
        for index in range(len(stable_pitches_cent_norm)):
            teoValue = teoNoteCent.values()[index]
            temp = TonicLastNote.find_nearest(teoNoteCent.values(), stable_pitches_cent_norm[index])
            for i in note_dict.keys():
                if int(note_dict[i]["Value"]) == temp:
                    note = u''.join(note_dict[i]["theoretical_name"]).encode('utf-8').strip()
                    performedNotes[i] = {"interval": {"value": stable_pitches_cent_norm[index]-(tonic_cent*ratio), "unit": "cent"},
                                         "stablepitch": {"value": stable_pitches[index], "unit": "Hz"},
                                         "symbol": i,
                                         "traditional_name": note}
        return performedNotes

    @staticmethod
    def plot(distribution, performedNotes):
        fig, ax1 = plt.subplots(1)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0.4)

        # plot title
        ax1.set_title('Pitch Distribution')
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Frequency of occurrence')

        # log scaling the x axis
        ax1.set_xscale('log', basex=2, nonposx='clip')
        ax1.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))

        # recording distribution
        ax1.plot(distribution.bins, distribution.vals, label='SongHist', ls='-', c='b', lw='1.5')

        # find tonic value, it will be drawn more prominently
        intervals = np.array(
            [abs(note['interval']['value']) for note in performedNotes.values()])
        if not len(np.where(intervals > 0.1)) == 1: # fuzzy 0 matching
            print 'Tonic is not present in stable pitches!'
        else:
            tonicInterval = np.min(intervals)

        # plot stable pitches
        for note in performedNotes.values():
            # find the value of the peak
            dists = np.array([abs(note['stablepitch']['value'] - bin) for bin in distribution.bins])
            peakind = np.argmin(dists)
            peakval = distribution.vals[peakind]

            # plot
            if note['interval']['value'] == tonicInterval:
                ax1.plot(note['stablepitch']['value'], peakval, 'cD', ms=10)
            else:
                ax1.plot(note['stablepitch']['value'], peakval, 'cD', ms=6, c='r')
            ax1.text(note['stablepitch']['value'], peakval, note['symbol'], style='italic', 
                horizontalalignment='center', verticalalignment='bottom')

        plt.show()

