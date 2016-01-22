note_model
==========

Introduction
------------
This repository contains tools to compute note models from audio pitch distribution analysis. Stable pitches which are extracted from pitch distribution ([here](https://github.com/hsercanatli/tonicidentifier_makam/blob/master/tonicidentifier/PitchDistribution.py)) are converted to cent value and normalized (transposed) to theoretical tonic value which is identified from makam name. For each stable pitches, nearest theoretical value is selected and its theoretical name is selected for output. 

Usage
=====
```python
from note_model.NoteModel import NoteModel

noteModel = NoteModel()

'''
distribution = PitchDistribution object (Please read the link above)
tonichz = Tonic frequency of recording in Hz
makam = Makam name of recording
'''

noteModel.calculate_notes(distribution, tonichz, makam)
```

Demo
====
Please refer to [this page](https://github.com/miracatici/note_model/blob/master/demo.ipynb) for an interactive demo.


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
