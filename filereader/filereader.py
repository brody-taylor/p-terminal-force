"""
Author: Brody Taylor
Date: Sept. 30, 2019
"""

import base64
import json as jsonparser
import numpy
import os.path as path
import struct
import xml.etree.cElementTree as xmlTree

from ecg import ECG, Lead


def read_file(file_path, seconds=None):
    """
    Reads digital ECG file.
    :param file_path: Path for digital ECG file
    :param seconds: Length of waveform in seconds to be read, default/None is entire waveform
    :return: ECG object
    """

    # Get file extension from path
    _, file_extension = path.splitext(file_path)

    # Call appropriate parser for file type
    match file_extension:
        case ".json":
            return json(file_path, seconds)

        case ".xml":
            # TODO: differentiate between different XML types (muse, scp)
            return muse(file_path, seconds)

        case ".dcm":
            return dicom(file_path, seconds)

        case "":
            raise Exception("Missing file extension")

        case _:
            raise Exception("File type not supported: '{}'".format(file_extension))


def json(file_path, seconds=2):
    """ For test data """

    # Pull data from JSON
    with open(file_path) as file:
        data = jsonparser.loads(file.read())
    freq = int(data["frequency"])

    # Get and extrapolate samples for each lead
    ecg = ECG(freq)
    for lead in Lead:
        if lead.value.lower() in data:
            samples = data[lead.value.lower()]
            while len(samples) < freq * seconds:
                samples = numpy.append(samples, samples[0:freq])
            ecg.set_lead(lead, samples)
    
    # Get and extrapolate annotion data
    anno = data["annotation"]
    qrs = [(anno["qrs"][0], anno["qrs"][1], anno["qrs"][2])]
    twave = [(anno["twave"][0], anno["twave"][1], anno["twave"][2])]
    pwave = [(anno["pwave"][0], anno["pwave"][1], anno["pwave"][2])]
    pterm = [anno["pterm"]]
    while len(qrs) < seconds:
        qrs.append((qrs[-1][0] + freq, qrs[-1][1] + freq, qrs[-1][2] + freq))
        twave.append((twave[-1][0] + freq, twave[-1][1] + freq, twave[-1][2] + freq))
        pwave.append((pwave[-1][0] + freq, pwave[-1][1] + freq, pwave[-1][2] + freq))
        pterm.append(pterm[0])
    ecg.set_qrs_complexes(qrs)
    ecg.set_t_waves(twave)
    ecg.set_p_waves(pwave)
    ecg.set_p_terminal_force(pterm)

    return ecg


def muse(file_path, seconds=None):
    """
    Extracts specified lead waveform from MUSE file type.
    :param file_path: Path to MUSE ECG file
    :param seconds: Length in seconds to be read, default/None is entire waveform
    :return: ECG object
    """

    xml_tree = xmlTree.parse(file_path)
    waveform_data = xml_tree.getroot().find("Waveform")
    all_leads = waveform_data.findall("LeadData")

    frequency = float(waveform_data.find("SampleBase").text)

    ecg = ECG(frequency)
    for lead_data in all_leads:
        lead_id = Lead.string_to_lead(lead_data.find("LeadID").text.lower())
        samples = decode_base64(lead_data.find("WaveFormData").text)
        if seconds and seconds < len(samples) / frequency:
            length = int(frequency * seconds)
            samples = samples[:length]
        ecg.set_lead(lead_id, numpy.array(samples))

    return ecg


def dicom(file_path, seconds=None):
    """
    Extracts specified lead waveform from DICOM file type
    :param file_path: Path to DICOM ECG file
    :param seconds: Length in seconds to be read, default/None is entire waveform
    :return: ECG object
    """

    " TODO: Implement DICOM compatibility "
    raise Exception("DICOM compatibility not yet implemented")


def scp(file_path, seconds=None):
    """
    Extracts specified lead waveform from SCP file type
    :param file_path: Path to SCP ECG file
    :param seconds: Length in seconds to be read, default/None is entire waveform
    :return: ECG object
    """

    " TODO: Implement SCP compatibility "
    raise Exception("SCP compatibility not yet implemented")


def decode_base64(encoded):
    """
    Decodes base64 encoded waveform.
    :param encoded: String of encoded waveform
    :return: List of samples in mV
    """

    # base64 string to byte array
    decoded = base64.b64decode(encoded)

    # convert byte array to list of samples, 16-bit signed
    samples = []
    for i in range(0, len(decoded), 2):
        samples.append(struct.unpack("<h", decoded[i:i+2])[0])

    return samples


def total_seconds_from_iso8601(time):
    """
    Converts time in format of hh:mm:ss.mmm to total seconds.
    :param time: String representing time in hh:mm:ss.mmm format
    :return: Integer representing total seconds
    """

    total_seconds = 0
    time_array = time.split(':')
    for index in range(len(time_array)):
        total_seconds += float(time_array[-(index + 1)]) * 60 ** index
    return total_seconds