"""
Author: Brody Taylor
Date: Sept. 30, 2019
"""

from argparse import ArgumentParser

import display
import dsp
import filereader
from ecg import Lead


def get_arguments():
    """ Defines and returns a dictionary of environment arguments """

    parser = ArgumentParser()

    # Argument for file path
    parser.add_argument("-f", "--file", required=True, help="Path to ECG file")

    # Argument for max duration of lead to be read
    parser.add_argument("-s", "--seconds", required=False, type=float, help="Maximum seconds to be displayed",
                        nargs='?', default=10)

    return vars(parser.parse_args())


def set_boundaries(ecg):
    frequency = ecg.get_frequency()
    qrs = dsp.determine_qrs(ecg.get_all_leads(), frequency)
    ecg.set_qrs_complexes(qrs)
    t_waves = dsp.determine_t_waves(ecg.get_all_leads(), frequency, qrs)
    ecg.set_t_waves(t_waves)
    p_waves = dsp.p_wave_boundaries(qrs, t_waves, ecg.get_lead(Lead.V1), frequency, do_filtering=True)
    ecg.set_p_waves(p_waves)
    p_terminal_force = dsp.pterm_measurements(ecg.get_lead(Lead.V1), frequency, p_waves, do_filtering=True)
    ecg.set_p_terminal_force(p_terminal_force)


def main():
    args = get_arguments()
    ecg = filereader.read_file(args["file"], args["seconds"])
    set_boundaries(ecg)
    display.plot(ecg, lead_of_interest=Lead.V1, annotate=True, do_filtering=True)


main()
