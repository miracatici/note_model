# -*- coding: utf-8 -*-
import json
import os
from morty.Converter import Converter
from tonicidentifier.toniclastnote import TonicLastNote
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker
from copy import deepcopy


class NoteModel(object):
    note_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    def __init__(self, pitch_threshold=50):
        self.pitch_threshold = pitch_threshold

    def calculate_notes(self, pitch_distribution, tonic_hz, makam):
        """
        Identifies the names of the performed notes from histogram peaks
        (stable pitches).
        """
        pd_copy = deepcopy(pitch_distribution)

        theoretical_intervals = self._get_theoretical_intervals_to_search(
            makam)

        try:  # convert the bins to hz, if they are given in cents
            pd_copy.cent_to_hz()
        except ValueError:
            pass

        # Calculate stable pitches
        peak_idx, peak_heights = pd_copy.detect_peaks()

        stable_pitches_hz = pd_copy.bins[peak_idx]
        stable_notes = self._stable_pitches_to_notes(
            stable_pitches_hz, theoretical_intervals, tonic_hz)

        return stable_notes

    def _stable_pitches_to_notes(self, stable_pitches_hz,
                                 theoretical_intervals, tonic_hz):
        stable_pitches_cent = Converter.hz_to_cent(stable_pitches_hz, tonic_hz)
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
                        theoretical_pitch = Converter.cent_to_hz(
                            note_cent, tonic_hz)
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
    def _is_same_pitch_class(n1, n2):
        return (n1[0] + n1[2:]) == (n2[0] + n2[2:])

    @staticmethod
    def _get_close_natural_notes(key_signature):
        close_near_flat = [ks[:2] for ks in key_signature if ks[3] == '1']

        return close_near_flat

    def _get_theoretical_intervals_to_search(self, makam):
        # Reading dictionary which contains note symbol, theoretical names and
        # their cent values
        note_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'data', 'note_dict.json')
        note_dict = json.load(open(note_file, 'r'))

        # Reading dictionary which contains theoretical information about each
        # makam
        makam_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'makam_extended.json')
        makam_dict = json.load(open(makam_file, 'r'))

        # get the key signature
        try:
            key_signature = self._get_extended_key_signature(
                makam_dict[makam]["key_signature"], note_dict)
        except KeyError:
            raise KeyError('Unknown makam')
        natural_notes = self._get_natural_notes(key_signature, note_dict)

        # Remove the notes neighboring the scale notes
        keep_notes = natural_notes + key_signature
        for note_name in note_dict.keys():
            if note_name in keep_notes:
                if note_name[2:4] in ['b5', 'b4']:
                    rm_note_symbol = self.note_letters[
                        (self.note_letters.index(note_name[0]) - 1) % 7]
                    rm_octave = note_name[1]
                    rm_notes = [rm_note_symbol + rm_octave + '#' + c
                                for c in ['4', '5']]
                elif note_name[2:4] in ['#5', '#4']:
                    rm_note_symbol = self.note_letters[
                        (self.note_letters.index(note_name[0]) + 1) % 7]
                    rm_octave = note_name[1]
                    rm_notes = [rm_note_symbol + rm_octave + 'b' + c
                                for c in ['4', '5']]
                else:
                    rm_notes = []

                for rm_note in rm_notes:
                    note_dict.pop(rm_note, None)

            elif len(note_name) == 2:  # there is a near accidental already
                note_dict.pop(note_name, None)
            elif len(note_name) == 4:
                if note_name[3] == '1':  # there is a near natural already
                    note_dict.pop(note_name, None)
                elif note_name[3] == '4':
                    if note_name[:3] + '5' in keep_notes:
                        note_dict.pop(note_name, None)
                    else:
                        pass
                elif note_name[3] == '5':  # remove the 5 commas
                    # if they are not in the kept notes
                    note_dict.pop(note_name, None)
                elif note_name[3] == '8':  # remove the 8 commas
                    # if they are not in the kept notes
                    note_dict.pop(note_name, None)
                else:
                    raise ValueError('Unhandled comma in ' + note_name)

        # recompute the cent values according to the tonic
        tonic_symbol = makam_dict[makam]["karar_symbol"]
        theoretical_intervals = {}
        for key, note in note_dict.iteritems():
            theoretical_intervals[key] = (note['Value'] -
                                          note_dict[tonic_symbol]['Value'])

        return theoretical_intervals

    def _get_natural_notes(self, key_signature, note_dict):
        close_natural_notes = self._get_close_natural_notes(key_signature)
        # get the natural notes that are not close to the key signature
        natural_notes = [n for n in note_dict.keys() if len(n) == 2 and n
                         not in close_natural_notes]
        return natural_notes

    def _get_extended_key_signature(self, key_sig_in, note_dict):
        key_signature = deepcopy(key_sig_in)
        for note in note_dict.keys():  # extend the key signature to octaves
            if len(note) > 2 and note not in key_signature and \
                    any([self._is_same_pitch_class(note, ks)
                         for ks in key_signature]):
                key_signature.append(note)

        return key_signature

    @staticmethod
    def plot(pitch_distribution, stable_notes):
        fig, ax = plt.subplots(1)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                            wspace=0, hspace=0.4)

        # copy the pitch distribution
        pd_copy = deepcopy(pitch_distribution)
        try:  # convert the bins to hz, if they are given in cents
            pd_copy.cent_to_hz()
        except ValueError:
            pass

        # plot title
        ax.set_title('Pitch Distribution')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Frequency of occurrence')

        # log scaling the x axis
        ax.set_xscale('log', basex=2, nonposx='clip')
        ax.xaxis.set_major_formatter(
            matplotlib.ticker.FormatStrFormatter('%d'))
        ax.set_xlim([min(pd_copy.bins), max(pd_copy.bins)])
        ax.set_xticks([note['stable_pitch']['value']
                       for note in stable_notes.values()])

        # recording distribution
        ax.plot(pd_copy.bins, pd_copy.vals,
                label='SongHist', ls='-', c='b', lw='1.5')

        # plot stable pitches
        NoteModel._plot_stable_pitches(ax, pd_copy, stable_notes)
        # define ylim higher than the highest peak so the note names have space
        plt.ylim([0, 1.2 * max(pd_copy.vals)])

    @staticmethod
    def _plot_stable_pitches(ax, pd_copy, stable_notes):
        for note_symbol, note in stable_notes.iteritems():
            # find the value of the peak
            dists = np.array([abs(note['stable_pitch']['value'] - dist_bin)
                              for dist_bin in pd_copy.bins])
            peak_ind = np.argmin(dists)
            peak_val = pd_copy.vals[peak_ind]

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
            txt_y_val = peak_val + 0.03 * max(pd_copy.vals)  # lift the
            # text a little bit
            ax.text(note['stable_pitch']['value'], txt_y_val, note_symbol,
                    style='italic', verticalalignment='bottom', rotation=60)
