"""
Author: Brody Taylor
Date: Sept. 30, 2019
"""

from enum import Enum


class ECG:
    def __init__(self, frequency):
        self._frequency = frequency

        # Initialize dict of leads and associated samples
        self._leads = {}

        # Initialize lists of waveform boundaries
        self._qrsComplexes = []
        self._t_waves = []
        self._p_waves = []

    def get_all_leads(self):
        return list(self._leads.values())

    def set_lead(self, lead, samples):
        # Validate lead
        if not isinstance(lead, Lead):
            raise TypeError('lead must be an instance of Lead')

        self._leads[lead] = samples

    def get_lead(self, lead):
        # Validate lead
        if not isinstance(lead, Lead):
            raise TypeError('lead must be an instance of Lead')

        if lead in self._leads:
            return self._leads[lead]

    def set_frequency(self, frequency):
        self._frequency = frequency

    def get_frequency(self):
        return self._frequency

    def set_qrs_complexes(self, boundaries):
        self._qrsComplexes = boundaries

    def get_qrs_complexes(self):
        return self._qrsComplexes

    def set_t_waves(self, boundaries):
        self._t_waves = boundaries

    def get_t_waves(self):
        return self._t_waves

    def set_p_terminal_force(self, p_terminal_force):
        self._p_terminal_force = p_terminal_force

    def get_p_terminal_force(self):
        return self._p_terminal_force

    def set_p_waves(self, boundaries):
        self._p_waves = boundaries

    def get_p_waves(self):
        return self._p_waves

    def __iter__(self):
        return iter(self._leads.values())

    def __len__(self):
        return len(self._leads)


class Lead(Enum):
    I   = "I"
    II  = "II"
    III = "III"
    V1  = "V1"
    V2  = "V2"
    V3  = "V3"
    V4  = "V4"
    V5  = "V5"
    V6  = "V6"
    AVL = "aVL"
    AVR = "aVR"
    AVF = "aVF"

    def string_to_lead(lead):
        """
        Maps a string representing a lead to the appropriate enum.
        :param lead: String representing the lead
        :return: Corresponding enum of type Lead
        """
        match str.lower(lead):
            case "i":
                return Lead.I
            case "ii":
                return Lead.II
            case "iii":
                return Lead.III
            case "avr":
                return Lead.III
            case "avl":
                return Lead.III
            case "avf":
                return Lead.III
            case "v1":
                return Lead.V1
            case "v2":
                return Lead.V2
            case "v3":
                return Lead.V3
            case "v4":
                return Lead.V4
            case "v5":
                return Lead.V5
            case "v6":
                return Lead.V6
