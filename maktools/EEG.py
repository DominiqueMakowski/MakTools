import mne
import numpy as np
import pandas as pd
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
def eeg_load(participant, path="data/", experiment="", system="brainvision", reference=None, stimdata_extension=".xlsx", stim_channel="PHOTO", treshold=0.04, upper=False, number=45, pause=None, after=0, before=None, condition1=None, condition2=None):
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
def eeg_plot_all(raw, events, event_id, eog_reject=600e-6, save=True, name="all", topo=False):
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
            fig.savefig('plots/all_' + str(name) +  '.png', format='png', dpi=1000)
        
        
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
            fig.savefig('plots/all_' + str(name) +  '.png', format='png', dpi=1000)
            
            
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
def eeg_ica(raw, method='fastica', n_components=20, random_state=23, plot=False):
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
def eeg_ssp(raw, plot=False):
    """
    """
    projs, eog_events = mne.preprocessing.compute_proj_eog(raw, average=True, n_grad=0, n_mag=0, n_eeg=2)
    eog_projs = projs[-2:]
    if plot is True:
        mne.viz.plot_projs_topomap(eog_projs, layout=mne.channels.find_layout(raw.info))
    raw.info['projs'] += eog_projs
    return(raw)