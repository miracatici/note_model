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
If you want to install the repository, it is recommended to install the package and dependencies into a virtualenv. In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then install the repo like this instead

    pip install -e .

Then you can install the rest of the dependencies:

    pip install -r requirements
    
Authors
-------
Bilge Miraç Atıcı	miracatici@gmail.com  
Sertan Şentürk		contact@sertansenturk.com
