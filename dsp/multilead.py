"""
Author: Brody Taylor
Date: Sept. 30, 2019
"""

import numpy

from .singlelead import qrs_boundaries, t_wave_boundaries, bandpass_filter, QRS_REFRACTORY_PERIOD


# Consensus thresholds are the minimum percent of leads that report a detection for it to be a consensus
QRS_CONSENSUS_THRESHOLD = 0.5
T_WAVE_CONSENSUS_THRESHOLD = 0.5


def determine_qrs(leads, frequency):
    """
    Multi-lead determination of QRS boundaries.
    Uses the single lead boundary method for each available lead and forms a consensus.
    :param leads: List of samples representing each available lead
    :param frequency: Sampling frequency
    :return: List of tuples containing the consensus start and end index for each QRS complex
    """

    # Array tracks the total number of leads that determined the index to be within a QRS complex
    qrs_complexes = numpy.zeros(len(leads[0]))

    for samples in leads:
        # Filter samples
        filtered = bandpass_filter(samples, frequency)

        # Get QRS boundaries for the lead
        boundaries = qrs_boundaries(filtered, frequency)

        # Add each QRS to the total
        for qrs in boundaries:
            start = qrs[0]
            end = qrs[1]
            for i in range(start, end + 1):
                qrs_complexes[i] += 1

    # Get consensus for qrs detections
    threshold = QRS_CONSENSUS_THRESHOLD * len(leads)
    consensus = build_consensus(qrs_complexes, threshold, refactory_period=QRS_REFRACTORY_PERIOD*frequency)

    return consensus


def determine_t_waves(leads, frequency, qrs):
    """
    Multi-lead determination of T-wave end points.
    Forms consensus for T-wave end-point using all available leads.
    :param leads: List of samples representing each available lead
    :param frequency: Sampling frequency
    :param qrs: List of tuples containing start and end index for QRS complexes
    :return: List of tuples containing the consensus start and end index for each T-wave
    """

    # Array tracks the total number of leads that determined the index to be within a T-wave
    t_waves = numpy.zeros(len(leads[0]))

    # Get T-wave end points for each lead
    for samples in leads:
        boundaries = t_wave_boundaries(qrs, samples, frequency)

        # Add each T-wave to the total
        for t_wave in boundaries:
            for i in range(t_wave[0], t_wave[-1] + 1):
                t_waves[i] += 1

    # Get boundary consensus
    threshold = T_WAVE_CONSENSUS_THRESHOLD * len(leads)
    consensus = build_consensus(t_waves, threshold)

    return consensus


def build_consensus(boundaries, threshold, refactory_period=None):
    """
    Finds the boundary consensus points between available leads.
    :param boundaries: Boundaries represented as intra-waveform occurrences at each index
    :param threshold: Number of occurrences to be considered a consensus
    :param refactory_period: Minimum samples between occurrences, where multiple consensuses within will be consolidated
    :return: List of tuples containing the consensus start and end indices
    """

    con_start = None
    con_end = None
    consensus = []
    for i in range(len(boundaries)):

        # Start recording boundaries if number of detections meet threshold
        if boundaries[i] >= threshold:
            if not con_start:
                con_start = i
            con_end = i

        # Record boundaries and reset for next
        elif con_start and con_end:
            consensus.append((con_start, con_end))
            con_start = None
            con_end = None

    # Add last consensus if needed
    if con_start and con_end:
        consensus.append((con_start, con_end))

    # Consolidate any gaps in the consensus if a refactory period is defined
    if refactory_period:
        consolidated = False
        while not consolidated:
            consolidated = True
            for i in range(1, len(consensus)):
                if consensus[i-1][0] + refactory_period > consensus[i][0]:
                    consolidated = False
                    new_qrs = (consensus[i-1][0], consensus[i][-1])
                    consensus[i-1] = new_qrs
                    consensus.pop(i)
                    break

    return consensus
