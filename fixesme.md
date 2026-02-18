🧩 TASK: Stabilize Python Runtime in ThonnySc
Step 1 — Remove Broken Embedded Python

Delete entire directory:

ThonnySc/_internal/


Remove:

python314.dll

_tkinter.pyd

Any manually copied DLLs

Any tcl/tk folders copied from other installs

Ensure no Python runtime is bundled.

Step 2 — Install Official Python 3.13.3

Download and install:

Python 3.13.3 (64-bit)

Enable:
✔ Add to PATH
✔ Install tcl/tk

Verify:

python --version
python -m tkinter


Tk window must open.

Step 3 — Modify Launcher To Use System Python

Change ThonnySc launcher to:

python -m thonny


Or if entry point is custom:

python -m thonnysc


Remove references to:

_internal/python.exe

Step 4 — Update Requirements

Create or update:

requirements.txt


Include only:

thonny
pyserial


Install dependencies using:

pip install -r requirements.txt

Step 5 — Force Interpreter Detection

In ThonnySc configuration:

Set default interpreter to:

CPython (system)


Remove any embedded interpreter configuration.

Step 6 — Clean Environment Variables

Ensure PATH does NOT contain:

python314.dll

old embedded Python

duplicate Python entries

Verify:

where python


Only Python 3.13.3 should appear.

Step 7 — Test ESP32 Backend

Open ThonnySc

Select:

MicroPython (ESP32)


Connect board

Confirm no:

INTERNAL ERROR
tkinter ImportError
DLL conflicts

🛡 Important Rules For The Agent

DO NOT manually copy DLLs.

DO NOT mix Python builds.

DO NOT use Python 3.14.

Use only official Python 3.13.3 full installation.

All compiled extensions must come from same interpreter.