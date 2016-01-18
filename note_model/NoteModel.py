# -*- coding: utf-8 -*-

import json
import makammusicbrainz as mmb
from tonic_identifier.PitchDistribution import hz_to_cent
from tonic_identifier.tonic_identifier import TonicLastNote


class NoteModel:
    performedNotes = {}

    def __init__(self, distribution, tonichz, makam):
            self.distribution = distribution
            self.makam = makam
            self.tonicHz = tonichz

    def calculate_notes(self):

        """
        :rtype: list
        """
        note_dict = json.load(open("note_dict.json", 'r'))
        makam_extended = json.load(open("makam_extended.json", 'r'))
        note_symbol = makam_extended[self.makam]["karar_symbol"]
        tonic_cent = hz_to_cent(self.tonicHz, 8.17579892 * 2)[0]
        teoretical_cent = int(note_dict[note_symbol][0])
        ratio = teoretical_cent / tonic_cent
        peaks = self.distribution.detect_peaks()
        peakId = peaks[0]
        stable_pitches = self.distribution.bins[peakId]
        stable_pitches_cent = hz_to_cent(stable_pitches, 8.17579892 * 2)
        stable_pitches_cent_norm = stable_pitches_cent * ratio
        teonotefreq = []

        for key in note_dict.keys():
            teonotefreq.append(int(note_dict[key][0]))
        for stable_cent in stable_pitches_cent_norm:
            temp = TonicLastNote.find_nearest(teonotefreq, stable_cent)
            for i in note_dict.keys():
                if int(note_dict[i][0]) == temp:
                    note = u''.join(note_dict[i][1]).encode('utf-8').strip()
                    print note
                    self.performedNotes[note] = {}

        return self.performedNotes

pitch = json.load(open("sample_data/1-04_ussak_taksim.json", 'r'))['pitch']
tonic_identifier = TonicLastNote()
tonic, pitch, pitch_chunks, distribution, sp = tonic_identifier.identify(pitch)
tonicHz = tonic["value"]
recDatas = mmb.getAudioMetadata("sample_data/1-04_ussak_taksim.json")
print recDatas
recMakam = recDatas["makam"][0]["mb_tag"]
print recMakam
nm = NoteModel(distribution, tonicHz, recMakam)
print nm.calculate_notes() #added from py
