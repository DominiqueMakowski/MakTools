import os
import pandas as pd
import numpy as np
import neurokit as nk
import mne
import biosppy
import matplotlib.pyplot as plt


participants = os.listdir("Data/")
participants.remove("Pilots")

clock = nk.Time()
for index, participant in enumerate(participants):
    print("-----------")
    print(participant)
    print(str(index/len(participants)*100) + "%, " + str(round(clock.get(reset=False)/1000/60, 2)) + "min")


    path = "Data/" + participant + "/"

    # List eeg and bio files
    eeg_files = os.listdir(path + "eeg/")
    bio_files = os.listdir(path + "bio/")

    # Read Anamnesis file
    df_anamnesis = nk.read_data("Anamnesis_Full", extension=".xlsx", participant_id=participant, path=path+ "/session1/")



#==============================================================================
# Read EEG
#==============================================================================
    raw = [s for s in eeg_files if "Rest" in s]
    raw = [s for s in raw if ".eeg" in s][0]
    raw = raw.replace('.eeg','')
    raw = nk.read_eeg(filename=raw, path=path + "eeg/", misc=["PHOTO"], reference=['TP7', 'TP9'])
    events = nk.find_events(nk.eeg_select_channels(raw, "PHOTO"), cut="lower")


    # Add ECG
    bio = [s for s in bio_files if "Rest" in s][0]
    bio = nk.read_acqknowledge(bio, path=path + "bio/")
    bio = nk.bio_process(ecg=bio["ECG, X, RSPEC-R"], add=bio["Photosensor"])["df"]
    bio_events = nk.find_events(bio["Photosensor"], cut="lower")
    raw = nk.eeg_add_channel(raw, bio["ECG_Filtered"], sync_index_raw=events["onsets"][0], sync_index_channel=bio_events["onsets"][0], channel_type="ecg", channel_name="ECG")


    # Crop
    beginning = raw.times[events["onsets"][0]]
    end = raw.times[events["onsets"][0]+events["durations"][0]]
#    raw.crop([beginning, end])



#==============================================================================
# Preprocessing
#==============================================================================


#    raw = nk.eeg_filter(raw, lowpass=0.016, highpass=80, notch=True, method="fir")
#
#    eog=True
#    ecg=True
#    method='fastica'
#    random_state=23
#    n_components=30
#    plot=False
#    raw, ica = nk.eeg_ica(raw)















#    epochs = nk.eeg_epoching(raw, nk.events, event_id=None, tmin=0, tmax=5, baseline=(None, None), detrend=1, eog_reject=None, drop_bad=False)





#        data = epochs.to_data_frame()
#        data["Bloc"] = index
#        df = pd.concat([df, data])
#    df = df.reset_index()
#
#    df2 = pd.DataFrame()
#    for bloc in set(df["Bloc"]):
#        for epoch in set(df[df["Bloc"]==bloc]["epoch"]):
#            data = df[(df["Bloc"]==bloc) & (df["epoch"]==epoch)]
#            data = list(data[nk.eeg_select_sensors(include="F", exclude=["C","T"])].mean(axis=1))
#            data = pd.DataFrame({str(bloc) + "_" + str(epoch):data})
#            df2 = pd.concat([df2, data], axis=1)
#    df2.index = range(-100, len(df2)-100)
#    nk.eeg_gfp()
#    df = df2.mean(axis=1)
#    df.plot()


#        epochs.to_data_frame(start=0.35, stop=0.6)



#    raw = raw.to_data_frame()
#    df = pd.DataFrame(raw[nk.eeg_select_sensors()].mean(axis=1))
#    df["ECG"] =  raw["ECG"]
#    df["Photosensor"] = raw["PHOTO"]
#
#    df = df[df["Photosensor"] < ((np.max(df["Photosensor"])-np.min(df["Photosensor"]))/2)]
#    rpeaks = nk.ecg_find_peaks(df["ECG"], 1000)
#
#
#    # HR = len(rpeaks)/(len(df)/1000/60)
#    df = df.reset_index().loc[rpeaks]
#

#    event_id = 999
#    ecg_events, _, _ = mne.preprocessing.find_ecg_events(raw, event_id, ch_name="FCz")
#    picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=False, eog=False,
#                       include=['FCz'], exclude='bads')
#    tmin, tmax = -0.1, 0.1
#    epochs = mne.Epochs(raw, ecg_events, event_id, tmin, tmax, picks=picks,
#                    proj=False)
#    data = epochs.get_data()
#
#    plt.plot(1e3 * epochs.times, np.squeeze(data).T)
#    plt.xlabel('Times (ms)')
#    plt.ylabel('ECG')
#    plt.show()

#==============================================================================
#   Read BIO
#==============================================================================
#    bio = [s for s in bio_files if "Interoception" in s][0]
#    bio = nk.read_acqknowledge(bio, path=path + "bio/")
#    bio = nk.bio_process(ecg=bio["ECG, X, RSPEC-R"], add=bio["Photosensor"])["Bio"]
#    bio_events = nk.find_events(bio["Photosensor"], cut="lower")


    # File containing Rest
#    raw = [s for s in eeg_files if "Interoception" in s]
#    raw = [s for s in raw if ".eeg" in s][0]
#    raw = raw.replace('.eeg','')
#    raw = nk.read_eeg(filename=raw, path=path + "eeg/", misc=["PHOTO"], reference=['TP7', 'TP9'])
#    events = nk.find_events(nk.eeg_select_channels(raw, "PHOTO"), cut="lower")
#
#    raw = nk.eeg_add_channel(raw, bio["ECG_Filtered"], sync_index_raw=events["onsets"][0], sync_index_channel=bio_events["onsets"][0], channel_type="ecg", channel_name="ECG")
##
##
#
#
##    durations = events["durations"]
#    events, event_id = nk.eeg_create_events(events["onsets"])
#    epochs = mne.Epochs(raw,
#                        events=events,
#                        event_id=event_id,
#                        tmin=0,
#                        tmax=15)
#    data = epochs.get_data()
#
#    d = []
#    for index, bloc in enumerate(data):
#        bloc = pd.DataFrame(bloc).T
#        bloc["Bloc"] = index
#        d.append(bloc)
#    data = pd.concat(d)
#    data["Mean"] = data[data.columns[0:63]].mean()
#
#    for i in set(data["Bloc"]):
#        data[data["Bloc"]==i][["Mean", 64, 65]].plot()
#
#    epochs = nk.eeg_epoching(raw, events, event_id, tmin=0, tmax=1, eog_reject=600e-3, drop_bad=False)





#    raw = nk.eeg_filter(raw, lowpass=1, highpass=30, method="fir")
#    event = nk.localize_events(nk.eeg_select_channels(raw, "PHOTO"), cut="lower", treshold=0.05)
#
#
#    signal = nk.eeg_select_channels(raw, nk.eeg_select_electrodes("C"))[58052:58052+300048]
#    signal = signal.mean(axis=1)
#    df = pd.DataFrame({"ECG":bio["Bio"]["ECG_Raw"],"EEG": signal})
#    epo = nk.create_epochs(df, bio["ECG_Features"]["ECG_R_Peaks"], 600, -200)
#
#    hb = pd.DataFrame()
#    eeg = pd.DataFrame()
#    for ep in epo:
#        hb = pd.concat([hb, epo[ep]["ECG"]], axis=1)
#        eeg = pd.concat([eeg, epo[ep]["EEG"]], axis=1)
#    hb = hb.mean(axis=1)
#    eeg = eeg.mean(axis=1)
#    hb = pd.concat([hb, eeg], axis=1)
#    nk.z_score(hb).plot()
#
#    [0:event["durations"][0]]
#    rpeaks = nk.eeg_find_Rpeaks(raw, "ECG")






#    bio = [s for s in bio_files if "Rest" in s][0]
#    bio = nk.read_acqknowledge(bio, path=path + "bio/")
#    bio = bio[bio["Photosensor"] < 3.5]
#    bio = nk.bio_process(ecg=bio["ECG, X, RSPEC-R"])
#
#
#    # File containing Rest
#    raw = [s for s in eeg_files if "Rest" in s]
#    raw = [s for s in raw if ".eeg" in s][0]
#    raw = raw.replace('.eeg','')
#    raw = nk.read_eeg(filename=raw, path=path + "eeg/", misc=["PHOTO"], reference=['TP7', 'TP9'])
#    raw = nk.eeg_filter(raw, lowpass=1, highpass=30, method="fir")
#    event = nk.localize_events(nk.eeg_select_channels(raw, "PHOTO"), cut="lower", treshold=0.05)
#
#
#    signal = nk.eeg_select_channels(raw, nk.eeg_select_electrodes("C"))[58052:58052+300048]
#    signal = signal.mean(axis=1)
#    df = pd.DataFrame({"ECG":bio["Bio"]["ECG_Raw"],"EEG": signal})
#    epo = nk.create_epochs(df, bio["ECG_Features"]["ECG_R_Peaks"], 600, -200)
#
#    hb = pd.DataFrame()
#    eeg = pd.DataFrame()
#    for ep in epo:
#        hb = pd.concat([hb, epo[ep]["ECG"]], axis=1)
#        eeg = pd.concat([eeg, epo[ep]["EEG"]], axis=1)
#    hb = hb.mean(axis=1)
#    eeg = eeg.mean(axis=1)
#    hb = pd.concat([hb, eeg], axis=1)
#    nk.z_score(hb).plot()
#
#    [0:event["durations"][0]]
#    rpeaks = nk.eeg_find_Rpeaks(raw, "ECG")



#    # File containing Rest
#    bio = [s for s in bio_files if "Rest" in s][0]
#    bio = nk.read_acqknowledge(bio, path=path + "bio/")
#    ecg = nk.bio_process(ecg=bio["ECG, X, RSPEC-R"], add=bio["Photosensor"])
#
##==============================================================================
##     Read EEG
##==============================================================================
#
#
#    # rename to read_eeg()
#    raw = nk.read_eeg(filename=raw, path=path + "eeg/", misc=["PHOTO"], reference=['TP7', 'TP9'])
#    # Add ECG
#    sync_index_raw = nk.localize_events(nk.eeg_select_channels(raw, "PHOTO"), cut="lower")["onsets"][0]
#    sync_index_channel = nk.localize_events(ecg["Bio"]["Photosensor"], cut="lower")["onsets"][0]
#    raw = nk.eeg_add_channel(raw, ecg["Bio"]["ECG_Filtered"], sync_index_raw=sync_index_raw, sync_index_channel=sync_index_channel, channel_type="ecg", channel_name="ECG")
#
#
##==============================================================================
## Preprocessing
##==============================================================================
#    # Select accurate period
#    event = nk.localize_events(nk.eeg_select_channels(raw, "PHOTO"), cut="lower")
#    beginning = raw.times[event["onsets"][0]]
#    end = raw.times[event["onsets"][0]+event["durations"][0]]
#    raw = raw.crop(beginning, end)
#
#    # Filter and Artifacts correction
##    raw = nk.eeg_filter(raw, lowpass=0.016, highpass=250, notch=True, method="fir")
#    raw = nk.eeg_filter(raw, lowpass=0.1, highpass=10, notch=True, method="fir")
#
##    raw.plot()
##    raw
##    eog=True
##    ecg=True
##    method='fastica'
##    n_components=30
##    random_state=23
##    plot=True
#
##    filtered = nk.eeg_ica(raw, eog=False, ecg=True, method='fastica', n_components=30, random_state=23, plot=True)
#
##==============================================================================
## Heart Beats Evoked
##==============================================================================
##    onsets = rpeaks
##    conditions=None
#    events, event_id = nk.eeg_create_events(nk.eeg_find_Rpeaks(raw, "ECG"))
#    epochs = nk.eeg_epoching(raw, events, event_id, tmin=-0.2, tmax=1, eog_reject=600e-3, drop_bad=False)
##    epochs.plot()
#    evoked = epochs.average()
#    evoked.copy().pick_channels(nk.eeg_select_electrodes(include="C", exclude="F")).plot()
#    raw.plot()
#
#event_id = 999
#ecg_events, _, _ = mne.preprocessing.find_ecg_events(raw, event_id)
#
## Read epochs
#picks = mne.pick_types(raw.info, meg=False, eeg=True, stim=False, eog=False, exclude='bads')
#tmin, tmax = -0.1, 0.1
#epochs = mne.Epochs(raw, ecg_events, event_id, tmin, tmax, picks=picks,proj=False)
#data = epochs.get_data()
#import matplotlib.pyplot as plt
#plt.plot(epochs.times, np.squeeze(data).T)
#plt.xlabel('Times (ms)')
#plt.ylabel('ECG')
#plt.show()
#    nk.eeg_select_channels(raw, "PHOTO").plot()

#    beginning =
#    end =
#    rest = rest.crop()
#    s1, time_index = rest.copy().pick_channels(["PHOTO"])[:]
#    s2, time_index = rest.copy().pick_channels(["Photosensor"])[:]
#
#    pd.Series(s1[0]).plot()
#    pd.Series(s2[0]).plot()
#    eeg_add_channel(raw, channel)


    # Inspect all channels
#    rest.plot()
    # Mark bad channels and, eventually, interpolate them
#    raw.info['bads'] = []
#    raw.interpolate_bads(reset_bads=False)
