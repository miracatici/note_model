note_model
==========

Introduction
------------
Repository for note modelling from pitch distribution peaks. Stable pitches which are extracted from pitch distribution 
are converted to cent value and normalized to theoretical tonic value which is identified from makam name. For each stable
pitches, nearest theoretical value is selected and its theoretical name is selected for output. 

Usage
=====
```python
from note_model.NoteModel import NoteModel

noteModel = NoteModel()

'''
distribution = PitchDistribution object
tonichz = Tonic frequency of recording in Hz
makam = Makam name of recording
'''

noteModel.calculate_notes(distribution, tonichz, makam)
```

Installation
============

Authors
-------
Bilge Miraç Atıcı	miracatici@gmail.com
Sertan Şentürk		contact@sertansenturk.com
