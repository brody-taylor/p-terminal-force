"""
Author: Brody Taylor
Date: Sept. 30, 2019
"""

import numpy

from dsp.dsp import *


# Non-pathogenic physiological features (in seconds)
QR_INTERVAL = 0.04
QRS_REFRACTORY_PERIOD = 0.2
QRS_WIDTH_MAX = 0.12  # prolonged QRS duration defined as ≥0.12 second
PR_INTERVAL_MAX = 0.22  # prolonged PR interval defined as ≥0.22 second
PR_INTERVAL_MIN = 0.12  # short PR interval defined as <0.12 second
P_WAVE_WIDTH_MAX = 0.12  # widened P-wave duration defined as ≥0.12 second

# Factor to determine if slopes are comparable for defining biphasic T-waves and P-waves
BIPHASIC_FACTOR = 1.5


def qrs_boundaries(samples, frequency, do_filtering=False):
    """
    Determines QRS complex boundaries in a waveform.
    :param samples: Array of waveform samples
    :param frequency: Sampling frequency
    :param do_filtering: Specifies if the provided samples need to be filtered
    :return: List of tuples containing start and end index for each QRS complex
    """

    # Filter samples if needed
    filtered = samples
    if do_filtering:
        filtered = bandpass_filter(samples, frequency)

    # Derives the waveform to get slope information
    derived = derivative_filter(filtered)

    # Gets list of detected QRS complexes
    detections = qrs_detect(derived, frequency)

    # Moving window average
    window = int(frequency * QRS_WIDTH_MAX)
    averaged = moving_average(squaring(derived), window)

    # Omit first detection if too close to start for accurate end-point determination
    if detections[0] < window:
        detections.pop(0)

    # Determine boundaries for each detection
    boundaries = []
    for detection in detections:

        # End-point is defined as local peak of the moving window average
        end_window = averaged[detection:detection+window]
        local_max = max(end_window)
        end = end_window.argmax()

        # Get start-point of R-wave as first point less than 5% of local peak when backtracking
        start_window = averaged[detection-window:detection]
        local_min = min(start_window)
        start_threshold = local_min + 0.05 * local_max
        start = numpy.where(start_window < start_threshold)[0][-1]

        # Get start-point of Q-wave by adjusting typical QR interval back from R-wave start
        start -= int(frequency * QR_INTERVAL)

        # Convert boundary indices from local to actual
        end += detection
        start += detection - window

        boundaries.append((start, end))

    return boundaries


def qrs_detect(derivative, frequency):
    """
    Detects QRS complexes using slope information.
    :param derivative: The derivative of the waveform
    :param frequency: Sampling frequency
    :return: List of indices representing where a complex was detected
    """

    BASE_CUTOFF_FACTOR = 0.8  # proportion of local slope max for detection cutoff
    LOWERED_CUTOFF_FACTOR = 0.5  # proportion of base detection cutoff to use for backtracking
    BACKTRACK_FACTOR = 1.8  # number of avg. inter-complex durations before initiating backtracking

    # Square slopes to non-linearly amplify QRS from other waves and to absolute the values
    squared = squaring(derivative)

    # Defines refractory period
    refract = int(frequency * QRS_REFRACTORY_PERIOD)

    # Set default heart rate of 50 beats per minute (in beats per second)
    hr = (50/60) * frequency

    # Get base cutoff from a 2-second max
    if int(2*frequency) < len(squared):
        cutoff = BASE_CUTOFF_FACTOR * max(squared[:int(2*frequency)])
    else:
        cutoff = BASE_CUTOFF_FACTOR * max(squared)

    detections = []
    num_samples = len(squared)
    i = -1
    while i < num_samples-1:
        i += 1
        found = False

        # Indicate QRS if above cutoff
        if squared[i] > cutoff:
            found = True

        # Initiate backtrack with lower threshold if too long without QRS
        elif detections and i > detections[-1] + BACKTRACK_FACTOR*hr:
            lower_cutoff = LOWERED_CUTOFF_FACTOR * cutoff
            for j in range(detections[-1]+refract, i):
                if squared[j] > lower_cutoff:
                    i = j
                    found = True
                    break

        if found:
            peak = get_peak(squared, i)
            detections.append(peak)

            # Update average heart rate
            if len(detections) > 1:
                hr = heart_rate(detections)

            # Update cutoff, weighted average between current and new
            cutoff = 0.8 * cutoff + 0.2 * (0.8 * squared[peak])

            # Skip the refractory period
            i = peak
            i += refract

    return detections


def t_wave_boundaries(qrs, samples, frequency, do_filtering=False):
    """
    Determines T-wave boundaries when given QRS boundaries.
    :param qrs: List of QRS boundaries
    :param samples: Array of waveform samples
    :param frequency: Sampling frequency
    :param do_filtering: Specifies if the provided samples need to be noise-filtered
    :return: List of tuples containing start and end index for T-waves
    """

    t_waves = []
    for window in t_wave_windows(qrs, frequency):
        win_start, win_end = window

        # Filter samples
        filtered = samples[win_start:win_end]
        if do_filtering:
            filtered = bandpass_filter(filtered, frequency)

        # Get slope information
        derived = squaring(derivative_filter(filtered), signed=True)

        up = derived.argmax()
        down = derived.argmin()
        peak_slope = max([abs(derived[up]), abs(derived[down])])

        # Classify between biphasic and monophasic T-wave and get last slope peak
        if up < down:
            # Can be up-down, down-up, or up
            end_peak = down
            if abs(max(derived[down:])) * BIPHASIC_FACTOR > peak_slope:
                # Adjust final slope peak if up-down
                end_peak += derived[down:].argmax()
        else:
            # Can be down-up, up-down, or down
            end_peak = up
            if abs(min(derived[up:])) * BIPHASIC_FACTOR > peak_slope:
                # Adjust final slope peak if down-up
                end_peak += derived[up:].argmin()

        # Define T-wave end-point forward from last slope peak until slope threshold
        threshold = derived[end_peak] / 10
        end = end_peak
        for i in range(end_peak, len(derived)):
            end = i
            if threshold > 0:
                if derived[i] < threshold:
                    break
            else:
                if derived[i] > threshold:
                    break

        # Convert end-point index from local to actual
        start = win_start
        end += win_start

        t_waves.append((start, end))

    return t_waves


def t_wave_windows(qrs, frequency):
    windows = []
    for i in range(len(qrs) - 1):
        # Define start of search window as QRS end-point plus ST interval
        win_start = qrs[i][-1] + int(0.04 * frequency)  # ST interval can range from 5 to 150 ms

        # Get average heart rate using previous 5 beats
        if i >= 4:
            hr = heart_rate([detection[0] for detection in qrs[i - 4:i + 1]])
        else:  # Use following beats if not enough have occurred
            if len(qrs) < 5:
                hr = heart_rate([detection[0] for detection in qrs])
            else:
                hr = heart_rate([detection[0] for detection in qrs[:5]])

        # Define end of search window as function of heart rate
        length = qrs[i + 1][0] - qrs[i][-1]
        if hr > 0.7 * frequency and length > int(0.5 * frequency):
            win_end = qrs[i][-1] + int(0.5 * frequency)
        elif length > int(0.7 * hr):
            win_end = qrs[i][-1] + int(0.7 * hr)
        else:
            win_end = qrs[i][-1] + int(0.7 * length)

        if win_end < win_start:  # TODO: wtf @twa52
            continue

        windows.append((win_start, win_end))
    return windows


def p_wave_boundaries(qrs, t_waves, samples, frequency, do_filtering=False):
    """
    Determines P-wave boundaries when given QRS boundaries and T-wave end-points.
    :param samples: Array of waveform samples
    :param frequency: Sampling frequency
    :param qrs: List of QRS boundaries
    :param t_waves: List of T-wave boundaries
    :param do_filtering: Specifies if the provided samples need to be filtered
    :return: List of tuples containing P-wave start, inflection (if biphasic), and end indices
    """

    # Filter samples if needed
    filtered = samples
    if do_filtering:
        filtered = bandpass_filter(samples, frequency)

    # Derives the waveform to get slope information
    derived = derivative_filter(filtered)

    p_waves = []
    for i in range(1, len(qrs)):

        # Get max slope of associated QRS complex
        qrs_slope = abs(max(derived[qrs[i][0]:qrs[i][-1]], key=abs))

        # Define search window
        win_start = qrs[i][0] - int(frequency * PR_INTERVAL_MAX)  # window starts at max P-R interval
        win_end = qrs[i][0]  # window goes until start of QRS complex

        # Adjust search window if it overlaps with T-wave
        for t_wave in t_waves:
            t_wave_end = t_wave[-1]
            if win_start < t_wave_end < win_end:
                win_start = t_wave_end

        # Filter window and get slope information
        if win_end - win_start < (frequency * PR_INTERVAL_MIN):  # window width must be at least the minimum P-R interval 
            continue
        win_derived = derived[win_start:win_end]

        # P-wave said to be present if negative slope peak is greater than 3% of max qrs slope
        neg_peak = numpy.argmin(win_derived)
        if abs(win_derived[neg_peak]) > 0.03 * qrs_slope:
            # Get forward and backward P-wave peaks if present
            for_zero_indices = numpy.where(win_derived[neg_peak:] > 0)[0]
            back_zero_indices = numpy.where(win_derived[:neg_peak] > 0)[0]
            if len(for_zero_indices) > 0 and len(back_zero_indices) > 0:
                for_zero = neg_peak + for_zero_indices[0]
                back_zero = back_zero_indices[-1]
            else:
                continue

            # Get forward and backward slope peaks
            if (peak_win := back_zero - int(P_WAVE_WIDTH_MAX * frequency)) > 0:
                back_peak = peak_win + win_derived[peak_win:back_zero].argmax()
            else:
                back_peak = win_derived[:back_zero].argmax()
            if (peak_win := for_zero + int(P_WAVE_WIDTH_MAX * frequency)) < len(win_derived):
                for_peak = for_zero + numpy.where(win_derived[for_zero:peak_win] == max(win_derived[for_zero:peak_win]))[0][-1]
            else:
                for_peak = for_zero + numpy.where(win_derived[for_zero:] == max(win_derived[for_zero:]))[0][-1]

            # Define P-wave start-point
            start = back_peak
            start_threshold = win_derived[back_peak] / 1.35
            for i in range(back_peak, -1, -1):
                start = i
                if win_derived[i] < start_threshold:
                    break

            # Define P-wave end-point and mid-point for biphasic classification
            if win_derived[for_peak] * BIPHASIC_FACTOR > win_derived[back_peak]:
                mid = neg_peak + win_start  # mid-point defined as the inflection between positive and negative wave
                end_threshold = win_derived[for_peak] / 2
                end = for_peak
                for j in range(for_peak, len(win_derived)):
                    end = j
                    if win_derived[j] < end_threshold:
                        break

            # Define P-wave end-point if monophasic classification, no mid-point
            else:
                mid = None
                end_threshold = win_derived[neg_peak] / 2
                end = neg_peak
                for j in range(neg_peak, len(win_derived)):
                    end = j
                    if win_derived[j] > end_threshold:
                        break

            # Convert start and end-point from local to actual
            start += win_start
            end += win_start

            if mid:
                p_waves.append((start, mid, end))
            else:
                p_waves.append((start, end))

    return p_waves


def pterm_measurements(samples, frequency, p_waves, do_filtering=False):
    """
    Calculates the P-terminal force when given P-wave boundaries.
    :param samples: Array of noise-filtered waveform samples
    :param frequency: Sampling frequency
    :param p_waves: List of tuples containing P-wave start, inflection (if biphasic), and end indices
    :param do_filtering: Specifies if the provided samples need to be filtered
    :return: List of P-terminal forces (in μV*mS) corresponding to provided P-waves
    """

    filtered = samples
    if do_filtering:
        filtered = bandpass_filter(samples, frequency)

    measurements = []
    for p_wave in p_waves:
        # P-terminal force is 0 if P-wave is monophasic
        if len(p_wave) < 3:
            measurements.append(0)
            continue

        start, mid, end = p_wave

        # Define duration as time between mid-point and end-point in mS
        duration = 1000 * (end - mid) / frequency

        # Create function for line connecting start-point and end-point
        x1 = start
        y1 = filtered[x1]
        x2 = end
        y2 = filtered[x2]
        m = (y1-y2)/(x1-x2)
        b = y1 - m * x1

        # Define depth as max absolute amplitude in μV
        depth = 0
        for i in range(mid, end):
            top = m * i + b
            bottom = filtered[i]
            if top - bottom > depth:
                depth = top - bottom
        depth = depth * 1000

        # P-terminal force is equal to the depth multiplied by the duration
        measurements.append(depth * duration)

    return measurements


def heart_rate(detections):
    """ Returns heart rate as average number of samples between QRS onsets """

    # Number of rates being averaged (denominator)
    rates = len(detections) - 1

    # Samples between first and last detection
    length = max(detections) - min(detections)

    return length / rates
