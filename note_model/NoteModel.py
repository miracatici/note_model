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
    def calculate_notes(distribution, tonichz, makam, threshold=50):
        """
        Identifies the names of the performed notes from histogram peaks (stable pitches).
        """
        # Reading dictionary which contains note symbol, theoretical names and their cent values
        note_file = os.path.join(os.path.dirname(os.path.abspath("note_dict.json")),
                                 'note_model/data', 'note_dict.json')  # os-independent path
        note_dict = json.load(open(note_file, 'r'))

        # Reading dictionary which contains theoretical information about each makam
        makam_file = os.path.join(os.path.dirname(os.path.abspath("makam_extended.json")),
                                  'note_model/data', 'makam_extended.json')  # os-independent path
        makam_extended = json.load(open(makam_file, 'r'))

        # Reading value from note_dict.json file
        notes_theo_cent = {}  # A dictionary for theoretical cent values of notes
        for key in note_dict.keys():
            notes_theo_cent[key] = (int(note_dict[key]["Value"]))

        # Defining tonic symbol from theoretical information
        tonic_theo_symbol = makam_extended[makam]["karar_symbol"]

        # Conversion hertz to cent, both of performed and theoretical values
        c0 = 16.35  # Reference is C0, unit is Hz
        tonic_perf_cent = hz_to_cent(tonichz, c0)[0]
        tonic_theo_cent = notes_theo_cent[tonic_theo_symbol]

        # Normalize ratio which is between theory and performance
        ratio = tonic_theo_cent / tonic_perf_cent

        # Calculate stable pitches
        peaks = distribution.detect_peaks()
        peak_id = peaks[0]

        stable_pitches_hz = distribution.bins[peak_id]

        stable_pitches_cent = hz_to_cent(stable_pitches_hz, c0)
        stable_pitches_cent_norm = stable_pitches_cent * ratio

        stable_pitches_cent_norm = sorted(stable_pitches_cent_norm)

        # Finding nearest theoretical values of each stable pitch, identify the name of this value and write to output
        performed_notes = {}  # Defining output (return) object

        for ind, pitch in enumerate(stable_pitches_cent_norm):
            temp = TonicLastNote.find_nearest(notes_theo_cent.values(), pitch)

            # print pitch, temp, ind, len(stable_pitches_cent_norm)
            if pitch - threshold < temp < pitch + threshold:
                # print pitch, temp, ind

                for key in note_dict.keys():
                    if int(note_dict[key]["Value"]) == temp:
                        # print note_dict[key]["Value"], temp, "\n"
                        note = u''.join(note_dict[key]["theoretical_name"]).encode('utf-8').strip()
                        performed_notes[key] = {"interval": {"value": pitch - (tonic_perf_cent * ratio),
                                                             "unit": "cent"},
                                                "stablepitch": {"value": stable_pitches_hz[ind],
                                                                "unit": "Hz"},
                                                "symbol": key,
                                                "traditional_name": note}
                        break

        return performed_notes

    @staticmethod
    def plot(distribution, performed_notes):
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
                [abs(note['interval']['value']) for note in performed_notes.values()])
        if not len(np.where(intervals > 0.1)) == 1:  # fuzzy 0 matching
            print 'Tonic is not present in stable pitches!'
        else:
            tonic_interval = np.min(intervals)

        # plot stable pitches
        for note in performed_notes.values():
            # find the value of the peak
            dists = np.array([abs(note['stablepitch']['value'] - bin) for bin in distribution.bins])
            peak_ind = np.argmin(dists)
            peak_val = distribution.vals[peak_ind]

            # plot
            if note['interval']['value'] == tonic_interval:
                ax1.plot(note['stablepitch']['value'], peak_val, 'cD', ms=10)
            else:
                ax1.plot(note['stablepitch']['value'], peak_val, 'cD', ms=6, c='r')
            ax1.text(note['stablepitch']['value'], peak_val, note['symbol'], style='italic',
                     horizontalalignment='center', verticalalignment='bottom')

        plt.show()
