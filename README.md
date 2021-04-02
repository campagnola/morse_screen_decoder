Morse Screen Decoder
====================

Select a region of your screen that is flashing, decode morse from the flashes. 
The decoder assumes a very good encoding; probably won't work for human-generated morse.

Instructions
------------

Run the script

    python morse_decoder.py

Then drag the red rectangle to cover the region of your screen with the signal in it. 
The decoded message should appear above the signal plot.


Requires
--------

- Python 3
- numpy
- scipy
- mss
- pyqtgraph


