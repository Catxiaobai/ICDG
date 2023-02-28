import re

s = 'EQ_60(17025323_55,AND_53(4294967295_48,DIV_47(CALLDATALOAD_15(0_13),PUSH29_16)))'
print(re.split('[(_,)]', s)[2])
