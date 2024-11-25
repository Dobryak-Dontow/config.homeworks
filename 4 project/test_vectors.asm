# Vector min operation test program
# Vector 1: starting at address 100
# Vector 2: starting at address 200
# Result: starting at address 300

# Load first vector
LOAD 2 42 100    # v1[0] = 42
LOAD 2 15 101    # v1[1] = 15
LOAD 2 73 102    # v1[2] = 73
LOAD 2 28 103    # v1[3] = 28
LOAD 2 91 104    # v1[4] = 91
LOAD 2 33 105    # v1[5] = 33
LOAD 2 67 106    # v1[6] = 67
LOAD 2 50 107    # v1[7] = 50

# Load second vector
LOAD 2 31 200    # v2[0] = 31
LOAD 2 89 201    # v2[1] = 89
LOAD 2 45 202    # v2[2] = 45
LOAD 2 76 203    # v2[3] = 76
LOAD 2 12 204    # v2[4] = 12
LOAD 2 65 205    # v2[5] = 65
LOAD 2 23 206    # v2[6] = 23
LOAD 2 94 207    # v2[7] = 94

# Calculate min for each pair
MIN 6 100 200 300    # result[0] = min(v1[0], v2[0])
MIN 6 101 201 301    # result[1] = min(v1[1], v2[1])
MIN 6 102 202 302    # result[2] = min(v1[2], v2[2])
MIN 6 103 203 303    # result[3] = min(v1[3], v2[3])
MIN 6 104 204 304    # result[4] = min(v1[4], v2[4])
MIN 6 105 205 305    # result[5] = min(v1[5], v2[5])
MIN 6 106 206 306    # result[6] = min(v1[6], v2[6])
MIN 6 107 207 307    # result[7] = min(v1[7], v2[7])
