# -*- coding: utf-8 -*-
import json
import os
from modetonicestimation.PitchDistribution import PitchDistribution
from modetonicestimation.ModeFunctions import hz_to_cent, cent_to_hz
from tonicidentifier.TonicLastNote import TonicLastNote
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker


class NoteModel:
    def __init__(self, pitch_threshold=50):
        self.pitch_threshold = pitch_threshold

    def calculate_notes(self, distribution, tonic_hz, makam):
        """
        Identifies the names of the performed notes from histogram peaks
        (stable pitches).
        """
        try:  # a dict is supplied, instantiate a distribution object
            distribution = PitchDistribution(distribution['bins'],
                                             distribution['vals'])
        except AttributeError:  
            pass
            
        # Reading dictionary which contains note symbol, theoretical names and
        # their cent values
        note_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'data', 'note_dict.json')
        note_dict = json.load(open(note_file, 'r'))

        # Reading dictionary which contains theoretical information about each
        # makam
        makam_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'makam_extended.json')
        makam_extended = json.load(open(makam_file, 'r'))

        # get the tonic symbol of the makam
        tonic_symbol = makam_extended[makam]["karar_symbol"]
        
        # recompute the cent values according to the tonic
        theoretical_intervals = {}
        for key, note in note_dict.iteritems():
            theoretical_intervals[key] = note['Value'] - \
                                         note_dict[tonic_symbol]['Value']
            
        # Temporary fix; the note symbols with b1, b8, #1, #8 are much less
        # frequent than the naturals. However because the theoretical
        # interval is so close to the natural these peaks are more to be
        # selected than the natural. To avoid this, we are removing the "b1"
        # and "#1"s from the search space for now. The code below should be
        # removed when this issue (#5) is fixed
        for key in theoretical_intervals.keys():
            is_one_comma = any(a in key for a in ['b1', 'b8', '#1', '#8'])
            if is_one_comma:
                theoretical_intervals.pop(key, None)

        # Calculate stable pitches
        peak_idx, peak_heights = distribution.detect_peaks()

        stable_pitches_hz = distribution.bins[peak_idx]
        stable_pitches_cent = hz_to_cent(stable_pitches_hz, tonic_hz)

        # Finding nearest theoretical values of each stable pitch, identify the
        # name of this value and write to output
        stable_notes = {}  # Defining output (return) object
        for stable_pitch_cent, stable_pitch_hz in zip(stable_pitches_cent,
                                                      stable_pitches_hz):
            note_cent = TonicLastNote.find_nearest(
                theoretical_intervals.values(), stable_pitch_cent)
            
            if abs(stable_pitch_cent - note_cent) < self.pitch_threshold:
                for key, val in theoretical_intervals.iteritems():
                    if val == note_cent:
                        theoretical_pitch = cent_to_hz(note_cent, tonic_hz)
                        stable_notes[key] = {
                            "performed_interval": {"value": stable_pitch_cent,
                                                   "unit": "cent"},
                            "theoretical_interval": {"value": note_cent,
                                                     "unit": "cent"},
                            "theoretical_pitch": {"value": theoretical_pitch,
                                                  "unit": "cent"},
                            "stable_pitch": {"value": stable_pitch_hz,
                                             "unit": "Hz"}}
                        break
                
        return stable_notes

    @staticmethod
    def plot(distribution, stable_notes):
        fig, ax = plt.subplots(1)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                            wspace=0, hspace=0.4)

        # plot title
        ax.set_title('Pitch Distribution')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Frequency of occurrence')

        # log scaling the x axis
        ax.set_xscale('log', basex=2, nonposx='clip')
        ax.xaxis.set_major_formatter(
            matplotlib.ticker.FormatStrFormatter('%d'))
        ax.set_xlim([min(distribution.bins), max(distribution.bins)])
        ax.set_xticks([note['stable_pitch']['value']
                       for note in stable_notes.values()])

        # recording distribution
        ax.plot(distribution.bins, distribution.vals,
                label='SongHist', ls='-', c='b', lw='1.5')

        # plot stable pitches
        for note_symbol, note in stable_notes.iteritems():
            # find the value of the peak
            dists = np.array([abs(note['stable_pitch']['value'] - dist_bin)
                              for dist_bin in distribution.bins])
            peak_ind = np.argmin(dists)
            peak_val = distribution.vals[peak_ind]

            # plot the theoretical frequency as a dashed line
            ax.vlines(x=note['theoretical_pitch']['value'], ymin=0,
                      ymax=peak_val, linestyles='dashed')

            # plot
            if note['performed_interval']['value'] == 0.0:
                ax.plot(note['stable_pitch']['value'], peak_val, 'cD', ms=10)
            else:
                ax.plot(note['stable_pitch']['value'], peak_val, 'cD', ms=6,
                        c='r')

            # print note name
            txt_y_val = peak_val + 0.03 * max(distribution.vals)  # lift the
            # text a little bit
            ax.text(note['stable_pitch']['value'], txt_y_val, note_symbol,
                    style='italic', verticalalignment='bottom', rotation=45)
            
        # define ylim higher than the highest peak so the note names have space
        plt.ylim([0, 1.2*max(distribution.vals)])
