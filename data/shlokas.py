# data/shlokas.py
from data.SECTION_1 import SECTION_1
from data.SECTION_2 import SECTION_2
from data.SECTION_3 import SECTION_3
from data.SECTION_4 import SECTION_4
from data.SECTION_5 import SECTION_5

# Combine sections: each SECTION_X is a list with one dict
ALL_SHLOKAS = [
    SECTION_1[0],
    SECTION_2[0],
    SECTION_3[0],
    SECTION_4[0],
    SECTION_5[0]
]

# For backward compatibility with earlier code
PROBLEM_SECTIONS = ALL_SHLOKAS

print("🔢 Current Sections Loaded:", len(ALL_SHLOKAS))
