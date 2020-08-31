import unittest

from dsp.dsp import *
from ecg import Lead
from .testing import *


class TestBandpassFilter(unittest.TestCase):
    def setUp(self):
        lead_of_interest = Lead.V1
        ecg = get_test_ecg()
        self.samples = ecg.get_lead(lead_of_interest)
        self.frequency = ecg.get_frequency()

    def test_happy_path(self):
        filtered = bandpass_filter(self.samples, self.frequency)

        self.assertEqual(len(filtered), len(self.samples))

    def test_small_sample_size(self):
        # Limit to half-second worth of samples
        num_samples = round(self.frequency * 0.5)
        samples = self.samples[:num_samples]

        filtered = bandpass_filter(samples, self.frequency)

        self.assertEqual(len(filtered), len(samples))


class TestDerivativeFilter(unittest.TestCase):
    def test_happy_path(self):
        # Generate samples with constant slope
        slope = -1.5
        samples = [5]
        [samples.append(samples[i] + slope) for i in range(999)]
        exp_derivative = [slope]*len(samples)

        derivative = derivative_filter(samples)

        self.assertEqual(len(derivative), len(samples))
        self.assertListEqual(list(derivative), exp_derivative)


class TestSquaring(unittest.TestCase):
    def test_happy_path_unsigned(self):
        samples = [0]
        [samples.append(samples[i] + 1) for i in range(999)]

        squared = squaring(samples)

        self.assertEqual(len(squared), len(samples))
        for i in range(len(samples)):
            self.assertEqual(squared[i], samples[i]**2)

    def test_happy_path_signed(self):
        samples = [0]
        [samples.append(samples[i] - 1) for i in range(999)]

        squared = squaring(samples, signed=True)

        self.assertEqual(len(squared), len(samples))
        for i in range(len(samples)):
            self.assertEqual(squared[i], -1*samples[i]**2)


class TestMovingAverage(unittest.TestCase):
    def test_happy_path(self):
        samples = [5]*1000

        moving_avg = moving_average(samples, 10)

        self.assertEqual(len(moving_avg), len(samples))
        self.assertListEqual(list(moving_avg), samples)


class TestGetPeak(unittest.TestCase):
    wave = [-3, -2, 0, 1, 2, 3, 2, 0, -3]
    peak = wave.index(max(wave))

    def test_happy_path_positive(self):
        samples = self.wave
        exp_peak = self.peak

        peak = get_peak(samples, 0)

        self.assertEqual(peak, exp_peak)

    def test_happy_path_negative(self):
        # Invert default wave from positive to negative
        samples = [i * -1 for i in self.wave]
        exp_peak = self.peak

        peak = get_peak(samples, 0, positive=False)

        self.assertEqual(peak, exp_peak)

    def test_multiple_waves(self):
        samples = self.wave * 3
        start = len(self.wave)

        exp_peak = len(self.wave) + self.peak

        peak = get_peak(samples, start)

        self.assertEqual(peak, exp_peak)


if __name__ == '__main__':
    unittest.main()
