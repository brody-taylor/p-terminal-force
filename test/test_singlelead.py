import unittest

from dsp.singlelead import *
from ecg import Lead
from .testing import *


class TestBoundary(unittest.TestCase):
    # ACCEPTABLE_RANGE is allowable time (in sec) that a determined boundary can be off from the actual, in either direction 
    ACCEPTABLE_RANGE = 0.015

    def setUp(self):
        self.lead_of_interest = Lead.V1
        self.ecg = get_test_ecg()

    def test_qrs_boundaries(self):
        exp = self.ecg.get_qrs_complexes()
        got = qrs_boundaries(
            self.ecg.get_lead(self.lead_of_interest),
            self.ecg.get_frequency(),
            do_filtering=True,
        )

        # Test detections
        self.assertFalse(false_negative(exp, got), "Missed QRS complex")
        self.assertFalse(false_positive(exp, got), "False QRS complex detection")

        # Test boundary accuracy
        self.assertLessEqual(
            boundary_accuracy(exp, got, self.ecg.get_frequency()),
            self.ACCEPTABLE_RANGE,
            "Determined QRS boundary outside of acceptable range",
        )

    def test_t_wave_boundaries_monophasic(self):
        # Use V5 for non-inverted monophasic T-wave
        self.lead_of_interest = Lead.V5

        exp = self.ecg.get_t_waves()[:-1]  # Only expect T-waves between QRS complexes
        got = t_wave_boundaries(
            self.ecg.get_qrs_complexes(),
            self.ecg.get_lead(self.lead_of_interest),
            self.ecg.get_frequency(),
            do_filtering=True,
        )

        # Test detections
        self.assertFalse(false_negative(exp, got), "Missed T-wave")
        self.assertFalse(false_positive(exp, got), "False T-wave detection")

        # Test boundary accuracy
        self.assertLessEqual(
            boundary_accuracy(exp, got, self.ecg.get_frequency(), do_start=False),
            self.ACCEPTABLE_RANGE,
            "Determined T-wave end-point outside of acceptable range",
        )

    def test_t_wave_boundaries_monophasic_inverted(self):
        exp = self.ecg.get_t_waves()[:-1]  # Only expect T-waves between QRS complexes
        got = t_wave_boundaries(
            self.ecg.get_qrs_complexes(),
            self.ecg.get_lead(self.lead_of_interest),
            self.ecg.get_frequency(),
            do_filtering=True,
        )

        # Test detections
        self.assertFalse(false_negative(exp, got), "Missed T-wave")
        self.assertFalse(false_positive(exp, got), "False T-wave detection")

        # Test boundary accuracy
        self.assertLessEqual(
            boundary_accuracy(exp, got, self.ecg.get_frequency(), do_start=False),
            self.ACCEPTABLE_RANGE,
            "Determined T-wave end-point outside of acceptable range",
        )

    def test_t_wave_boundaries_biphasic_inverted(self):
        # Use test data with biphasic T-wave
        self.ecg = get_test_ecg(test_data=BIPHASIC)

        exp = self.ecg.get_t_waves()[:-1]  # Only expect T-waves between QRS complexes
        got = t_wave_boundaries(
            self.ecg.get_qrs_complexes(),
            self.ecg.get_lead(self.lead_of_interest),
            self.ecg.get_frequency(),
            do_filtering=True,
        )

        # Test detections
        self.assertFalse(false_negative(exp, got), "Missed T-wave")
        self.assertFalse(false_positive(exp, got), "False T-wave detection")

        # Test boundary accuracy
        self.assertLessEqual(
            boundary_accuracy(exp, got, self.ecg.get_frequency(), do_start=False),
            self.ACCEPTABLE_RANGE,
            "Determined T-wave end-point outside of acceptable range",
        )

    def test_t_wave_boundaries_biphasic_inverted(self):
        # Use test data with biphasic T-wave
        self.ecg = get_test_ecg(test_data=BIPHASIC)
        self.lead_of_interest = Lead.V5

        exp = self.ecg.get_t_waves()[:-1]  # Only expect T-waves between QRS complexes
        got = t_wave_boundaries(
            self.ecg.get_qrs_complexes(),
            self.ecg.get_lead(self.lead_of_interest),
            self.ecg.get_frequency(),
            do_filtering=True,
        )

        # Test detections
        self.assertFalse(false_negative(exp, got), "Missed T-wave")
        self.assertFalse(false_positive(exp, got), "False T-wave detection")

        # Test boundary accuracy
        self.assertLessEqual(
            boundary_accuracy(exp, got, self.ecg.get_frequency(), do_start=False),
            self.ACCEPTABLE_RANGE,
            "Determined T-wave end-point outside of acceptable range",
        )

    def test_p_wave_boundaries_biphasic(self):
        exp = self.ecg.get_p_waves()[1:]  # Only expect P-waves between QRS complexes
        got = p_wave_boundaries(
            self.ecg.get_qrs_complexes(),
            self.ecg.get_t_waves(),
            self.ecg.get_lead(self.lead_of_interest),
            self.ecg.get_frequency(),
            do_filtering=True,
        )

        # Test detections
        self.assertFalse(false_negative(exp, got), "Missed P-wave")
        self.assertFalse(false_positive(exp, got), "False P-wave detection")

        # Test boundary accuracy
        self.assertLessEqual(
            boundary_accuracy(exp, got, self.ecg.get_frequency()),
            self.ACCEPTABLE_RANGE,
            "Determined P-wave boundaries outside of acceptable range",
        )

    def test_p_wave_boundaries_monophasic(self):
        # Use V5 for monophasic P-wave
        self.lead_of_interest = Lead.V5

        exp = self.ecg.get_p_waves()[1:]  # Only expect P-waves between QRS complexes
        got = p_wave_boundaries(
            self.ecg.get_qrs_complexes(),
            self.ecg.get_t_waves(),
            self.ecg.get_lead(self.lead_of_interest),
            self.ecg.get_frequency(),
            do_filtering=True,
        )

        # Test detections
        self.assertFalse(false_negative(exp, got), "Missed P-wave")
        self.assertFalse(false_positive(exp, got), "False P-wave detection")

        # Test boundary accuracy
        self.assertLessEqual(
            boundary_accuracy(exp, got, self.ecg.get_frequency()),
            self.ACCEPTABLE_RANGE,
            "Determined P-wave boundaries outside of acceptable range",
        )

    def test_p_terminal_force_measurements(self):
        exp = self.ecg.get_p_terminal_force()
        got = pterm_measurements(
            self.ecg.get_lead(Lead.V1),
            self.ecg.get_frequency(),
            self.ecg.get_p_waves(),
            do_filtering=True,
        )

        self.assertEqual(len(exp), len(got), "Did not get expected number of measurements")
        self.assertLessEqual(
            measurement_accuracy(exp, got),
            self.ACCEPTABLE_RANGE,
            "Determined P-terminal force outside of acceptable range",
        )


class TestHeartRate(unittest.TestCase):
    def test_happy_path(self):
        exp_rate = 100
        indices = [10]
        [indices.append(indices[i] + exp_rate) for i in range(9)]

        rate = heart_rate(indices)

        self.assertEqual(rate, exp_rate)


if __name__ == '__main__':
    unittest.main()
