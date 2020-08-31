"""
Author: Brody Taylor
Date: Sept. 30, 2019
"""

import math
import numpy
import scipy.signal as signal
import scipy.stats as stats
import statistics


def bandpass_filter(samples, frequency):
    # Savitzky–Golay filter to remove electromyogenic noise
    filtered = signal.savgol_filter(samples, 31, 3, mode='nearest')

    # Highpass filter to remove baseline wander
    filtered = highpass_filter(filtered, frequency)

    return filtered


def highpass_filter(samples, frequency, cutoff=0.8):
    """
    Butterworth second-order sections high-pass filter.
    :param samples: Array of samples to be filtered
    :param frequency: Sampling frequency
    :param cutoff: Cutoff in Hz
    :return: Array of filtered samples
    """

    # Get Nyquist frequency
    nyq = 0.5 * frequency

    # Get normalized cut-off frequencies
    normalized_cutoff = cutoff / nyq

    # Get second-order filter coefficients
    sos = signal.butter(1, normalized_cutoff, analog=False, btype='highpass', output='sos')

    # Use sosfiltfilt vs sosfilt to eliminate phase delay by using forward-backward filtering
    filtered = signal.sosfiltfilt(sos, samples)

    return filtered


def derivative_filter(samples):
    """ Gets the derivative of a waveform """

    window = 2

    derivative = numpy.empty(len(samples))
    x = [i for i in range(0, (window * 2) + 1)]
    for i in range(window, len(samples) - window):
        y = samples[i-window:i+window+1]
        slope, *_ = stats.linregress(x, y)
        derivative[i] = slope

    # Extrapolate over sample delay
    for i in range(window):
        derivative[i] = derivative[window]
        derivative[-(1+i)] = derivative[-(window+1)]

    return derivative


def squaring(samples, signed=False):
    """
    Squares each sample in an array.
    :param samples: Array of samples to be squared
    :param signed: Can specify if value should keep original sign, default is false
    :return: Array of squared samples
    """

    squared = numpy.empty(len(samples))
    if signed:
        for i in range(len(samples)):
            sample = samples[i]
            if sample < 0:
                squared[i] = -1 * (sample ** 2)
            else:
                squared[i] = sample ** 2
    else:
        for i in range(len(samples)):
            squared[i] = samples[i] ** 2

    return squared


def moving_average(samples, width):
    """
    Moving window averaging.
    :param samples: Array of samples to be averaged
    :param width: Number of samples in the moving window
    :return: Array of averages
    """

    averages = numpy.empty(len(samples))

    # Extrapolate samples for delay, weights first sample by amount of window overhang
    for i in range(width):
        averages[i] = statistics.mean([samples[0] for _ in range(width - i)] + [sample for sample in samples[:i]])

    for i in range(width, len(samples)):
        averages[i] = statistics.mean(samples[i-width:i])

    return averages


def get_peak(samples, index, positive=True):
    """
    Given a point on a wave, will find the peak.
    :param samples: Array of waveform samples
    :param index: Index of any point on the wave
    :param positive: Can indicate whether wave is positive or negative, default is positive
    :return: Index of the wave peak
    """

    # Inverts sign if negative
    if positive:
        wave = samples
    else:
        wave = [sample * -1 for sample in samples]

    # Determines if peak is to the left or right
    if index > 0:
        direction = int(math.copysign(1, wave[index] - wave[index-1]))
    else:
        direction = int(math.copysign(1, wave[index+1] - wave[index]))

    # Finds last point of rising edge
    i = index + direction
    peak = index
    while 0 <= i < len(wave):
        if wave[i] < wave[i-direction]:
            break
        peak = i
        i += direction

    return peak
