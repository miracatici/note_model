# -*- coding: utf-8 -*-

import json
import os
from tonic_identifier.PitchDistribution import hz_to_cent
from tonic_identifier.tonic_identifier import TonicLastNote


class NoteModel:

    def __init__(self):
        pass

    @staticmethod
    def calculate_notes(distribution, tonichz, makam):

        note_file = os.path.join(os.path.dirname(os.path.abspath("note_dict.json")), 'note_model/data', 'note_dict.json')
        note_dict = json.load(open(note_file, 'r'))
        makam_file = os.path.join(os.path.dirname(os.path.abspath("makam_extended.json")), 'note_model/data', 'makam_extended.json')
        makam_extended = json.load(open(makam_file, 'r'))
        note_symbol = makam_extended[makam]["karar_symbol"]
        c0 = 16.35
        tonic_cent = hz_to_cent(tonichz, c0)[0]
        teoretical_cent = int(note_dict[note_symbol][0])
        ratio = teoretical_cent / tonic_cent
        peaks = distribution.detect_peaks()
        peakId = peaks[0]
        stable_pitches = distribution.bins[peakId]
        stable_pitches_cent = hz_to_cent(stable_pitches, c0)
        stable_pitches_cent_norm = stable_pitches_cent * ratio
        teonotefreq = []
        performedNotes = {}

        for key in note_dict.keys():
            teonotefreq.append(int(note_dict[key][0]))
        for stable_cent in stable_pitches_cent_norm:
            temp = TonicLastNote.find_nearest(teonotefreq, stable_cent)
            for i in note_dict.keys():
                if int(note_dict[i][0]) == temp:
                    note = u''.join(note_dict[i][1]).encode('utf-8').strip()
                    print note
                    performedNotes[note] = {}

        return performedNotes


