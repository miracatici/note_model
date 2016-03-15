note_model
==========
Tools to compute note models from audio pitch distribution analysis

Introduction
------------
This repository contains tools to compute note models from audio pitch distribution analysis. Stable pitches which are extracted from pitch distribution are converted to cent value and normalized (transposed) to theoretical tonic value which is identified from makam name. For each stable pitches, nearest theoretical value is selected and its theoretical name is selected for output. 

Usage
------
```python

    import json
    
    from pitchfilter.PitchFilter import PitchFilter
    from tonicidentifier.TonicLastNote import TonicLastNote
    from note_model.NoteModel import NoteModel
    
    '''
    distribution = PitchDistribution object (Code is linked above)
    tonichz = Tonic frequency of recording in Hz
    makam = Makam name of recording
    '''
    
    # inputs; pitch track and makam of the recording
    rec_makam = "nihavent"  
    pitch = json.load(open("sample_data/feda89e3-a50d-4ff8-87d4-c1e531cc1233.json", 'r'))['pitch']
    
    # Extra: Postprocess the pitch track to get rid of spurious pitch estimations and correct octave errors
    flt = PitchFilter()    # Code is here: https://github.com/hsercanatli/pitch-post-filter
    pitch = flt.run(pitch)
    
    # run tonic identification using last note detection
    tonic_identifier = TonicLastNote()    # Code is here https://github.com/hsercanatli/tonicidentifier_makam
    tonic, pitch, pitch_chunks, distribution, sp = tonic_identifier.identify(pitch)
    tonic_hz = tonic["value"]
    
    # Obtain the the stable notes
    model = NoteModel()
    stablenotes, theo_peaks = model.calculate_notes(distribution, tonic_hz, rec_makam)
```

Demo
------------
Please refer to [this page](https://github.com/miracatici/note_model/blob/master/demo.ipynb) for an interactive demo.


Installation
------------
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
