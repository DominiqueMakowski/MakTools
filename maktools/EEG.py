import mne
import nolds  # Fractal
import numpy as np
import pandas as pd
import re
import matplotlib
from matplotlib import pyplot as plt
import neuropsydia as n
n.start(False)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def see_channel(channel, ticks=50):
    """
    """
    data, times = channel[:]
    plt.clf()
    plt.figure(figsize=(40,4))
    plt.xticks(list(range(0,int(max(times)),50)))
    plt.plot(times, data.T)
    plt.show()
#    plt.savefig('plot.png', format='png', dpi=1000)
#    plt.savefig('foo.png')


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def load_brainvision_raw(participant, path="data/", experiment="", system="brainvision", reference=None):
    """
    """
    if system == "brainvision":
        extension = ".vhdr"
    raw = mne.io.read_raw_brainvision(path + participant + "/" + participant + "_" + experiment + extension, eog=('HEOG', 'VEOG'), misc=['PHOTO'], montage="easycap-M1", preload=True)
    if reference is None:
        raw.set_eeg_reference()
    else:
        raw.set_eeg_reference(reference)
    return(raw)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def add_events(raw, participant, path="data/", stimdata_extension=".xlsx", experiment="", stim_channel="PHOTO", treshold=0.04, upper=False, number=45, pause=None, after=0, before=None, condition1=None, condition2=None):
    """
    """
    signal, time_index = raw.copy().pick_channels([stim_channel])[:]
    if pause is not None:
        after = pause
        before = pause
    events_onset, events_time = n.select_events(signal[0],
                                            treshold=treshold,
                                            upper=upper,
                                            time_index=time_index,
                                            number=number,
                                            after=after,
                                            before=before)
    trigger_list = pd.read_excel(path + participant + "/" + participant + "_" + experiment + stimdata_extension)
    trigger_list = trigger_list.sort_values("Order")

    triggers = {}
    if pause is not None:
            triggers[condition1] = trigger_list[condition1][0:number*2]
            triggers[condition2] = trigger_list[condition2][0:number*2]
    if condition2 is None:
        events_list = list(triggers[condition1])
    else:
        events_list = list(triggers[condition1] + "/" + triggers[condition2])


    events, event_id = n.create_mne_events(events_onset, events_list)
    raw.add_events(events, stim_channel="STI 014")
    return(raw, events, event_id)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_load(participant, path="", experiment="", system="brainvision", reference=None, stimdata_extension=".xlsx", stim_channel="PHOTO", treshold=0.04, upper=False, number=45, pause=None, after=0, before=None, condition1=None, condition2=None):
    """
    """
    raw = load_brainvision_raw(participant, path=path, experiment=experiment, system=system, reference=reference)

    raw, events, event_id = add_events(raw=raw,
                                           participant=participant,
                                           path=path,
                                           stimdata_extension=stimdata_extension,
                                           experiment=experiment,
                                           stim_channel=stim_channel,
                                           treshold=treshold,
                                           upper=upper,
                                           number=number,
                                           pause=pause,
                                           after=after,
                                           before=before,
                                           condition1=condition1,
                                           condition2=condition2)
    return(raw, events, event_id)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_plot_all(raw, events, event_id, eog_reject=600e-6, save=True, name="all", topo=False, path=""):
    """
    """
    reject = {
#        "eeg": 4000e-13,
        "eog": eog_reject  # Adjust with caution
        }
    # picks
    picks = mne.pick_types(raw.info,
                       meg=False,
                       eeg=True,
                       eog=True,
                       stim=False,
                       exclude='bads',
#                       selection=O_cluster + PO_cluster
                       )

    # epochs
    epochs = mne.Epochs(raw,
                        events=events,
                        event_id=event_id,
                        tmin=-0.2,
                        tmax=1,
                        picks=picks,
                        add_eeg_ref=True,
                        reject_by_annotation=True,
                        reject=reject,  # Adjust values carefully
                        proj=True,  # With SSP projections
                        detrend=1,  # "None", 1: Linear detrend, 0 DC detrend,
                        baseline=(None, 0)  #
                        )

    # Drop bads
    epochs.drop_bad()


    # Plot
    if topo is False:
        fig = mne.combine_evoked([epochs.average()]).plot_joint()
        if save is True:
            fig.savefig(path + str(name) +  '.png', format='png', dpi=1000)


    if topo is True:
        fig = mne.viz.plot_evoked_topo([epochs.average()],
        #                                  fig_background="black",
                                          fig_facecolor="black",
        #                                  conditions = ['Negative', 'Neutral'],
    #                                      scalings=dict(eeg=1e1),
                                          layout=mne.channels.find_layout(raw.info),
                                          font_color="black",
                                          axis_facecolor="black",
    #                                      proj = "interactive",
                                          color='red'
        #                                  layout_scale = 2
                                          )
        if save is True:
            fig.savefig(path + str(name) +  '.png', format='png', dpi=1000)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_filter(raw, lowpass=1, highpass=40, notch=True, method="iir"):
    if notch == True:
        raw.notch_filter(np.arange(50, 201, 50),
                         phase='zero',
                         method=method
                         )
    raw.filter(lowpass,
               highpass,
               method=method)
    return(raw)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_eog_ica(raw, method='fastica', n_components=20, random_state=23, plot_sources=False, plot=False):
    """
    """
    ica = mne.preprocessing.ICA(n_components=n_components,
                                method=method,  # for comparison with EEGLAB try "extended-infomax" here
                                random_state=random_state  # random seed
                                )

    picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=True, ecg=False, stim=False, exclude='bads')
    ica.fit(raw, picks=picks, decim=3)

    # create one EOG trials
    eog_epochs = mne.preprocessing.create_eog_epochs(raw,
                                                     picks=picks)
    # find via correlation the ICA components
    eog_inds, scores = ica.find_bads_eog(eog_epochs)

    if plot_sources==True:
        ica.plot_sources(raw)

    ica.exclude.extend(eog_inds)
    raw = ica.apply(raw)

    if plot is True:
        ica.plot_components()[0]
    return(raw)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_eog_ssp(raw, plot=False):
    """
    """
    projs, eog_events = mne.preprocessing.compute_proj_eog(raw, average=True, n_grad=0, n_mag=0, n_eeg=2)
    eog_projs = projs[-2:]
    if plot is True:
        mne.viz.plot_projs_topomap(eog_projs, layout=mne.channels.find_layout(raw.info))
    raw.info['projs'] += eog_projs
    return(raw)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_eog_window(raw, duration=0.5):
    """
    Cover the whole blink with full duration.
    """
    average_eog = mne.preprocessing.create_eog_epochs(raw).average()
    print('We found %i EOG events' % average_eog.nave)

    eog_events = mne.preprocessing.find_eog_events(raw)
    n_blinks = len(eog_events)
    onset = eog_events[:, 0] / raw.info['sfreq'] - (duration/2)
    duration = np.repeat(duration, n_blinks)
    raw.annotations = mne.Annotations(onset,
                                      duration,
                                      ['bad blink'] * n_blinks,
                                      orig_time=raw.info['meas_date'])
    return(raw)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_epoching(raw, events, event_id, tmin=-0.2, tmax=1, eog_reject=600e-6, proj=True, detrend=1, drop_bad=True, remove_eog=True, baseline=(None, 0)):
    """
    """
    if eog_reject is not None:
        # Peak-to-peak rejection parameters (amplitude ranges as floats)
        reject = {"eog": eog_reject}
    else:
        reject = None

    picks = mne.pick_types(raw.info,
                           meg=False,
                           eeg=True,
                           eog=True,
                           stim=False,
                           exclude='bads'
                           )

    epochs = mne.Epochs(raw,
                        events=events,
                        event_id=event_id,
                        tmin=tmin,
                        tmax=tmax,
                        picks=picks,
                        add_eeg_ref=True,
                        reject_by_annotation=True,
                        reject=reject,  # Adjust values carefully
                        proj=proj,  # With SSP projections
                        detrend=detrend,  # "None", 1: Linear detrend, 0 DC detrend,
                        baseline=baseline,
                        preload = True
                        )

    # Drop bads
    if drop_bad == True:
        epochs.drop_bad()

    if remove_eog == True:
        epochs.pick_types(meg=False, eeg=True)
    return(epochs)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_fractal_dim(epochs, entropy=True, hurst=True, dfa=False, lyap_r=False, lyap_e=False):
    """
    """

    df = epochs.to_data_frame(index=["epoch", "time", "condition"])

    # Separate indexes
    index = df.index.tolist()
    epochs = []
    times = []
    events = []
    for i in index:
        epochs.append(i[0])
        times.append(i[1])
        events.append(i[2])



    data = {}
    if entropy == True:
        data["Entropy"] = {}
    if hurst == True:
        data["Hurst"] = {}
    if dfa == True:
        data["DFA"] = {}
    if lyap_r == True:
        data["Lyapunov_R"] = {}
    if lyap_e == True:
        data["Lyapunov_E"] = {}


    n.time.reset()
    for epoch in set(epochs):
        subset = df.loc[epoch]

        if entropy == True:
            data["Entropy"][epoch] = []
        if hurst == True:
            data["Hurst"][epoch] = []
        if dfa == True:
            data["DFA"][epoch] = []
        if lyap_r == True:
            data["Lyapunov_R"][epoch] = []
        if lyap_e == True:
            data["Lyapunov_E"][epoch] = []



        for channel in subset:
            if entropy == True:
                data["Entropy"][epoch].append(nolds.sampen(subset[channel]))
            if hurst == True:
                data["Hurst"][epoch].append(nolds.hurst_rs(subset[channel]))
            if dfa == True:
                data["DFA"][epoch].append(nolds.dfa(subset[channel]))
            if lyap_r == True:
                data["Lyapunov_R"][epoch].append(nolds.lyap_r(subset[channel]))
            if lyap_e == True:
                data["Lyapunov_E"][epoch].append(nolds.lyap_e(subset[channel]))

        if entropy == True:
            data["Entropy"][epoch] = np.mean(data["Entropy"][epoch])
        if hurst == True:
            data["Hurst"][epoch] = np.mean(data["Hurst"][epoch])
        if dfa == True:
            data["DFA"][epoch] = np.mean(data["DFA"][epoch])
        if lyap_r == True:
            data["Lyapunov_R"][epoch] = np.mean(data["Lyapunov_R"][epoch])
        if lyap_e == True:
            data["Lyapunov_E"][epoch] = np.mean(data["Lyapunov_E"][epoch])


        time = n.time.get(reset=False)/1000
        time = time/(epoch+1)
        time = (time * (len(set(epochs))-epoch))/60
        print(str(round((epoch+1)/len(set(epochs))*100,2)) + "% complete, remaining time: " + str(round(time, 2)) + 'min')

    df = pd.DataFrame.from_dict(data)

    list_events = []
    for i in range(len(events)):
        list_events.append(events[i] + "_" + str(epochs[i]))

    list_events = n.remove_following_duplicates(list_events)
    list_events = [re.sub('_\d+', '', i) for i in list_events]
    df["Epoch"] = list_events
    return(df)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_topo_erp(evoked, line_colors=("red"), line_width=0.5, background_color="black", font_color="white", save=False, name="topo_erp", dpi=1000):
    """
    """
    fig = mne.viz.plot_evoked_topo(evoked,
                               fig_facecolor=background_color,
                               axis_facecolor=background_color,
                               font_color=font_color,
                               show=False,
                               color=line_colors)

    fig.subplots_adjust(hspace=5)  # Not sure it changes anything though.
    for line in fig.findobj(matplotlib.lines.Line2D):
        line.set_linewidth(line_width)

    fig.show()
    if save == True:
        fig.savefig(name + ".png", format='png', dpi=dpi)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_select_electrodes(include="all", exclude=None, hemisphere="both", include_central=True):
    """
    """
    sensors = ['AF3', 'AF4', 'AF7', 'AF8', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'CP1', 'CP2', 'CP3', 'CP4', 'CP5', 'CP6', 'CPz', 'Cz', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'FC1', 'FC2', 'FC3', 'FC4', 'FC5', 'FC6', 'Fp1', 'Fp2', 'FT10', 'FT7', 'FT8', 'FT9', 'O1', 'O2', 'Oz', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'PO3', 'PO4', 'PO7', 'PO8', 'POz', 'Pz', 'FCz', 'T7', 'T8', 'TP10', 'TP7', 'TP8', 'TP9', 'AFz']

    if include != "all":
        sensors = [s for s in sensors if include in s]

    if exclude != None:
        if isinstance(exclude, str):
            exclude = [exclude]
        for to_exclude in exclude:
            sensors = [s for s in sensors if to_exclude not in s]

    if hemisphere != "both":
        if include_central == False:
            if hemisphere == "left":
                sensors = [s for s in sensors if "1" in s or "3" in s or "5" in s or "7" in s or "9" in s]
            if hemisphere == "right":
                sensors = [s for s in sensors if "2" in s or "4" in s or "6" in s or "8" in s or "10" in s]
        else:
            if hemisphere == "left":
                sensors = [s for s in sensors if "1" in s or "3" in s or "5" in s or "7" in s or "9" in s or "z" in s]
            if hemisphere == "right":
                sensors = [s for s in sensors if "2" in s or "4" in s or "6" in s or "8" in s or "10" in s or "z" in s]


    return(sensors)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_average_per_epoch(epochs, include="all", exclude=None, hemisphere="both", include_central=True, time_start=0, time_end=0.4):
    """
    """
    epochs.pick_channels(eeg_select_electrodes(include=include, exclude=exclude, hemisphere=hemisphere, include_central=include_central))


    df = epochs.to_data_frame(index=["epoch", "time", "condition"])

    # Separate indexes
    index = df.index.tolist()
    epochs = []
    times = []
    events = []
    for i in index:
        epochs.append(i[0])
        times.append(i[1])
        events.append(i[2])