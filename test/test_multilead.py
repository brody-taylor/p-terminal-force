import unittest

from dsp.multilead import *
from .testing import *


class TestBoundary(unittest.TestCase):
    # ACCEPTABLE_RANGE is allowable time (sec) that a determined boundary can be off from the actual, in either direction 
    ACCEPTABLE_RANGE = 0.015

    def setUp(self):
        self.ecg = get_test_ecg()

    def test_determine_qrs(self):
        exp = self.ecg.get_qrs_complexes()
        got = determine_qrs(
            self.ecg.get_all_leads(),
            self.ecg.get_frequency(),
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
    
    def test_determine_t_waves(self):
        exp = self.ecg.get_t_waves()[:-1]  # Only expect T-waves between QRS complexes
        got = determine_t_waves(
            self.ecg.get_all_leads(),
            self.ecg.get_frequency(),
            self.ecg.get_qrs_complexes(),
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


if __name__ == '__main__':
    unittest.main()
