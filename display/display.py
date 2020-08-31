"""
Author: Brody Taylor
Date: Sept. 30, 2019
"""

from matplotlib import pyplot

from dsp.singlelead import bandpass_filter as filter
from ecg import Lead


# Graph color settings
GRID_LINE_COLOR = "grey"
LEAD_COLOR = "red"
QRS_COLOR = "blue"
T_WAVE_COLOR = "green"
P_WAVE_COLOR = "orange"


def plot(ecg, lead_of_interest=Lead.V1, annotate=True, do_filtering=False, grid_lines=True):
    """
    Plots the lead of interest.
    :param ecg: ECG object containing the samples
    :param lead_of_interest: Lead enum specifying the lead that will be displayed
    :param annotate: Boolean for displaying the QRS, T-Wave, and P-Wave annotation
    :param do_filter: Boolean specifying if samples should be filtered before they are displayed
    :param grid_lines: Boolean for displaying grid lines
    """

    frequency = ecg.get_frequency()
    samples = ecg.get_lead(lead_of_interest)
    if do_filtering:
        samples = filter(samples, frequency)

    # Determine graph boundaries
    y_min = min(samples)
    y_max = max(samples)
    x_min = 0
    x_max = len(samples)

    # Configure the display
    pyplot.gcf().set_size_inches(18, 7)
    pyplot.axis("off")
    pyplot.tight_layout()
    x, y = get_grid_size(frequency)
    pyplot.gca().set_aspect(x/y)

    # Sets x-axis limit before scrolling
    max_display = int(frequency * 2)
    if x_max > max_display:
        pyplot.xlim([0, max_display])

    # Draw grid lines
    if grid_lines:
        draw_grid_lines(frequency, x_min, x_max, y_min, y_max)

    # Annotate the display
    if annotate:
        draw_boundaries(ecg.get_qrs_complexes(), y_min, y_max, QRS_COLOR, highlight=True)
        draw_boundaries(ecg.get_t_waves(), y_min, y_max, T_WAVE_COLOR, highlight=True)
        draw_boundaries(ecg.get_p_waves(), y_min, y_max, P_WAVE_COLOR)
        write_p_terminal_force(ecg.get_p_terminal_force(), ecg.get_p_waves(), samples, frequency)

    # Plot the lead
    pyplot.plot([i for i in range(x_max)], samples, linestyle="solid", color=LEAD_COLOR)

    pyplot.show()
    p_waves = []
    for boundary in ecg.get_p_waves():
        p_waves.append((boundary[0], boundary[-1]))
    return p_waves


def draw_grid_lines(frequency, x_min, x_max, y_min, y_max):
    grid_width, grid_height = get_grid_size(frequency)

    # Vertical lines
    for i in range(x_min + grid_width, x_max, grid_width):
        if i % (grid_width * 5) == 0:  # bold every 5 lines
            pyplot.plot([i, i], [y_min, y_max], linestyle="solid", color=GRID_LINE_COLOR, linewidth=2)
        else:
            pyplot.plot([i, i], [y_min, y_max], linestyle="solid", color=GRID_LINE_COLOR, linewidth=1)

    # Horizontal lines
    num_hlines = int((y_max - y_min) / grid_height) + 1
    for i in range(num_hlines):
        y1 = i * grid_height + y_min
        y2 = i * grid_height + y_min
        if i % 5 == 0:  # bold every 5 lines
            pyplot.plot([x_min, x_max], [y1, y2], linestyle="solid", color=GRID_LINE_COLOR, linewidth=2)
        else:
            pyplot.plot([x_min, x_max], [y1, y2], linestyle="solid", color=GRID_LINE_COLOR, linewidth=1)


def get_grid_size(frequency):
    grid_width = int(frequency * 0.04)  # one line represents 4 ms
    grid_height = 0.1  # one line represents 0.1 mV
    return grid_width, grid_height


def draw_boundaries(boundaries, y_min, y_max, color, highlight=False):
    for boundary in boundaries:
        start, end = boundary[0], boundary[-1]
        if highlight and start != end:
            highlight = pyplot.Rectangle((start, y_min), end - start, y_max - y_min, color=color)
            pyplot.gca().add_patch(highlight)
        else:
            pyplot.plot([start, start], [y_min, y_max], linestyle="dashed", color=color, linewidth=1)
            pyplot.plot([end, end], [y_min, y_max], linestyle="dashed", color=color, linewidth=1)


def write_p_terminal_force(p_terminal_force, p_waves, samples, frequency):
    for i in range(len(p_waves)):
        p_wave = p_waves[i]
        
        # Build text
        pterm = str(round(p_terminal_force[i], 2))
        if pterm == "0":
            pterm = "N/A"
        else:
            pterm += " μV*mS"

        # Get x-coord for text
        if len(p_wave) > 3:
            x = p_wave[1]
        else:
            x = p_wave[0] + round((p_wave[-1] - p_wave[0]) / 2)
        
        # Get y-coord for text
        _, grid_y = get_grid_size(frequency)
        y = min(samples[p_wave[0]:p_wave[-1]]) - 2 * grid_y

        box = bbox=dict(facecolor="white")
        pyplot.text(x, y, pterm, fontsize=10, ha="center", bbox=box)
