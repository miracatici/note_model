notemodel
==========
Tools to compute note models from audio pitch distribution analysis

Introduction
------------
This repository contains tools to compute note models from audio pitch distribution analysis. Stable pitches which are extracted from pitch distribution are converted to cent value and normalized (transposed) to theoretical tonic value which is identified from makam name. For each stable pitches, nearest theoretical value is selected and its theoretical name is selected for output. 

Usage
------
```python

    import json
    
    from pitchfilter.pitchfilter import PitchFilter
    from tonicidentifier.toniclastnote import TonicLastNote
    from notemodel.notemodel import NoteModel
    from modetonicestimation.pitchdistribution import PitchDistribution
    
    '''
    pitch = a n x 3 matrix of pitch values, where rows indicate time, pitch and confidence
    tonichz = Tonic frequency of recording in Hz
    rec_makam = Makam name of recording
    '''
    
    # inputs; pitch track and makam of the recording
    rec_makam = "huseyni"
    pitch_file = 'huseyni--sazsemaisi--aksaksemai----tatyos_efendi/8b8d697b-cad9-446e-ad19-5e85a36aa253.json'
    pitch = json.load(open(pitch_file, 'r'))['pitch']
    
    # Extra: Postprocess the pitch track to get rid of spurious pitch estimations and correct octave errors
    flt = PitchFilter()    # The code is here: https://github.com/hsercanatli/pitch-post-filter
    pitch = flt.run(pitch)

    # run tonic identification using last note detection
    tonic_identifier = TonicLastNote()    # The code is here: https://github.com/hsercanatli/tonicidentifier_makam
    tonic = tonic_identifier.identify(pitch)[0]  # don't use the distribution output from here, it is only
    # computed from the end of the recording
    tonic_hz = tonic["value"]
    
    # compute the pitch distribution
    pitch_distribution = PitchDistribution.from_hz_pitch(pitch[:,1], ref_freq=tonic['value'])
    
    # Obtain the the stable notes
    model = NoteModel()
    stablenotes, theo_peaks = model.calculate_notes(pitch_distribution, tonic_hz, rec_makam, 
                                                    min_peak_ratio=0.1)

    # plot the result
    model.plot(pitch_distribution, stablenotes)
    pylab.show()
```

Demo
------------
Please refer to [demo.ipynb](https://github.com/miracatici/note_model/blob/master/demo.ipynb) for an interactive demo.


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
