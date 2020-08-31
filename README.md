# Measuring P-wave Terminal Force in V1 #

This program is for measuring the P-terminal force of the V1 lead. The P-terminal force is the product of the duration and amplitude of the negative terminal deflection of the P-wave.

Increased P-terminal force in V1 can signify left atrial cardiopathy, a precursor to atrial fibrillation and a risk factor for stroke [1].

Accurate and time-efficient measuring of the P-terminal force in V1 is important for conducting research on the link between left atrial cardiopathy and stroke risk, and on the effectiveness of anticoagulants in preventing stroke in patients with left atrial cardiopathy.

Author: **Brody Taylor**<br>
Project Supervisor: **Dr. Luciano Sposato**<br>
Program Supervisor: **Dr. Candace Gibson**<br>
**Medical Health Informatics**<br>
**University of Western Ontario**

## How to Use ##

To display an ECG file and its measurements, run `main.py`

| Parameter | Type | Required | Description |
|-|-|-|-|
| -f, --file | String | Yes | Path to ECG file |
| -s, --seconds | Float | No | Max duration to be displayed |

To run using test data:
```
python main.py -f test/testdata/nsr.json
```

### Display ###

| Waveform | Indicator |
|-|-|
| QRS Complex | Blue highlight |
| T-wave | Green highlight |
| P-wave | Dotted orange boundary lines |

For P-waves where a negative terminal deflection is detected, the P-terminal force will be calculated and displayed below the waveform.

## Methodology ##

Measuring the P-terminal force follows these steps:

1. QRS complex detection and boundary determination
2. T-wave endpoint determination 
3. P-wave detection, classification, and boundary determination
4. Measurement of the P-wave negative terminal deflection if present

For improved accuracy, steps 1 and 2 do a multi-lead analysis, where detections and boundaries are determined for all available leads and then used to form a consensus.

## References ##

1. Kamel, Z., Soliman, R., Heckbert, A., Kronmal, M., Longstreth, M., Nazarian, M., & Okin, M. (2014). P-Wave Morphology and the Risk of Incident Ischemic Stroke in the Multi-Ethnic Study of Atherosclerosis. *Stroke, 45*, 2786–2788.
