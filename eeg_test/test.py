import mne

raw = mne.io.read_raw_fif("example_raw.fif", preload=True) # Data corresponds to 5 min of EEG resting state recording.

#==============================================================================
# Problems with crop
#==============================================================================
# Convert to time in seconds
beginning = 51.521999999999998
end = 351.58800000000002
# crop
raw.crop(beginning, end)

print(raw.first_samp)
# prints 51522. Shoudn't it print 0? If not, how to reinitialize it?



#==============================================================================
# Problems with ICA
#==============================================================================

raw.filter(1, 40)  # 1Hz high pass is often helpful for fitting ICA

picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=False, stim=False, exclude='bads')


ica = mne.preprocessing.ICA(n_components=25, method='fastica', random_state=23)
ica.fit(raw, picks=picks, decim=3)

ecg_epochs = mne.preprocessing.create_ecg_epochs(raw, tmin=-.5, tmax=.5)
ecg_inds, scores = ica.find_bads_ecg(ecg_epochs, method='ctps')
ica.plot_properties(ecg_epochs, picks=ecg_inds, psd_args={'fmax': 35.})


"""
Got the following:


  File "<ipython-input-1-6a52256cec99>", line 1, in <module>
    runfile('E:/Dropbox/RECHERCHE/Misc/MakTools/eeg_test/test.py', wdir='E:/Dropbox/RECHERCHE/Misc/MakTools/eeg_test')

  File "C:\Users\DomM\Desktop\WinPython-32bit-3.5.3.0Qt5\python-3.5.3\lib\site-packages\spyder\utils\site\sitecustomize.py", line 866, in runfile
    execfile(filename, namespace)

  File "C:\Users\DomM\Desktop\WinPython-32bit-3.5.3.0Qt5\python-3.5.3\lib\site-packages\spyder\utils\site\sitecustomize.py", line 102, in execfile
    exec(compile(f.read(), filename, 'exec'), namespace)

  File "E:/Dropbox/RECHERCHE/Misc/MakTools/eeg_test/test.py", line 32, in <module>
    ecg_inds, scores = ica.find_bads_ecg(ecg_epochs, method='ctps')

  File "<string>", line 2, in find_bads_ecg

  File "C:\Users\DomM\Desktop\WinPython-32bit-3.5.3.0Qt5\python-3.5.3\lib\site-packages\mne\utils.py", line 707, in verbose
    return function(*args, **kwargs)

  File "C:\Users\DomM\Desktop\WinPython-32bit-3.5.3.0Qt5\python-3.5.3\lib\site-packages\mne\preprocessing\ica.py", line 1036, in find_bads_ecg
    sources = self.get_sources(inst).get_data()

  File "C:\Users\DomM\Desktop\WinPython-32bit-3.5.3.0Qt5\python-3.5.3\lib\site-packages\mne\preprocessing\ica.py", line 726, in get_sources
    sources = self._sources_as_epochs(inst, add_channels, False)

  File "C:\Users\DomM\Desktop\WinPython-32bit-3.5.3.0Qt5\python-3.5.3\lib\site-packages\mne\preprocessing\ica.py", line 776, in _sources_as_epochs
    sources = self._transform_epochs(epochs, concatenate)

  File "C:\Users\DomM\Desktop\WinPython-32bit-3.5.3.0Qt5\python-3.5.3\lib\site-packages\mne\preprocessing\ica.py", line 652, in _transform_epochs
    data = np.hstack(epochs.get_data()[:, picks])

  File "C:\Users\DomM\Desktop\WinPython-32bit-3.5.3.0Qt5\python-3.5.3\lib\site-packages\numpy\core\shape_base.py", line 288, in hstack
    return _nx.concatenate(arrs, 1)

MemoryError
"""
