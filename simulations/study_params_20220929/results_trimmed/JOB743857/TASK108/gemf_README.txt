This file contains general helpful information about the GEMF output.

=== output.txt ===
This is the main file of interest. It contains the GEMF simulation output. The columns of the output file are as follows (in the exact order):
* Time of event
* Total rate
* Node that was infected
* Previous state of the node
* New state of node
* Number of nodes in each state (one column per state)
* Comma-delimited lists of inducer nodes from each state (one state per list)

=== State Number Translations ===
NS = 0
S = 1
I1 = 2
I2 = 3
I3 = 4
I4 = 5
A1 = 6
A2 = 7
A3 = 8
A4 = 9
D = 10
