import filereader


NORMAL_SINUS_RHYTHM = "./test/testdata/nsr.json"
BIPHASIC = "./test/testdata/biphasic.json"


def get_test_ecg(seconds=5, test_data=NORMAL_SINUS_RHYTHM):
    return filereader.read_file(test_data, seconds=seconds)


def false_negative(exp_boundaries, got_boundaries):
    missed = False
    for exp in exp_boundaries:
        found = False
        if len(exp) == 3:
            exp_mid = exp[1]
        else:
            exp_mid = int(exp[-1] - exp[0] / 2)

        for got in got_boundaries:
            start, end = got[0], got[-1]
            if start < exp_mid < end:
                found = True
                break

        if not found:
            missed = True

    return missed


def false_positive(exp_boundaries, got_boundaries):
    false_detection = False
    for got in got_boundaries:
        start, end = got[0], got[-1]
        found = False
        for exp in exp_boundaries:
            if len(exp) == 3:
                exp_mid = exp[1]
            else:
                exp_mid = int(exp[-1] - exp[0] / 2)

            if start < exp_mid < end:
                found = True

        if not found:
            false_detection = True

    return false_detection


def boundary_accuracy(exp_boundaries, got_boundaries, frequency, do_start=True, do_end=True):
    max_offset = 0
    for i in range(len(got_boundaries)):
        exp = exp_boundaries[i]
        got = got_boundaries[i]

        # Check start-point
        start_offset = abs(exp[0] - got[0]) / frequency
        if do_start and start_offset > max_offset:
            max_offset = start_offset

        # Check end-point
        end_offset = abs(exp[-1] - got[-1]) / frequency
        if do_end and end_offset > max_offset:
            max_offset = end_offset
    
    return max_offset


def measurement_accuracy(exp_measurements, got_measurements):
    max_inaccuracy = 0
    for i in range(len(got_measurements)):
        exp = exp_measurements[i]
        got = got_measurements[i]
        diff = abs(exp - got) / got
        if diff > max_inaccuracy:
            max_inaccuracy = diff
    return max_inaccuracy
