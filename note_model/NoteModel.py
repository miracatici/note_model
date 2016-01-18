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
        c0 = 16.35                                                              # Reference is C0, unit is Hz
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
                    performedNotes[i] = {"interval": {"Value": stable_pitches_cent_norm[index]-(tonic_cent*ratio), "Unit": "cent"},
                                         "stablepitch": {"Value": stable_pitches[index], "Unit": "Hz"},
                                         "Symbol": i,
                                         "traditional_name": note}
        return performedNotes


