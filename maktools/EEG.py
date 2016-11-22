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
def load_eeg(participant, path="data/", experiment="", system="brainvision", reference=None, stimdata_extension=".xlsx", stim_channel="PHOTO", treshold=0.04, upper=False, number=45, pause=None, after=0, before=None, condition1=None, condition2=None):
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