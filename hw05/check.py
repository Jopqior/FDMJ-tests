import glob
import os
from typing import Tuple

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def parse_line(line: str) -> Tuple[int, int]:
    """
    Parse the line to extract line number and column number.
    Returns a tuple (line_number, column_number).
    """
    parts = line.strip().split(" ")
    return int(parts[0][6:]), int(parts[1][4:-1])


def compare_files(file1_path: str, file2_path: str) -> bool:
    """
    Compare two files according to the specified conditions:
    - Both files contain either empty lines or a single line with the same content.
    - If there is content in the single line, it should have the same format.
    """
    with open(file1_path, "r") as file1, open(file2_path, "r") as file2:
        lines1 = file1.readlines()
        lines2 = file2.readlines()

        # Remove leading and trailing whitespace, and empty lines
        lines1 = [line.strip() for line in lines1 if line.strip()]
        lines2 = [line.strip() for line in lines2 if line.strip()]

        if len(lines1) != len(lines2):
            return False

        if len(lines1) == 0:
            return True

        # Compare line and column numbers
        return parse_line(lines1[0]) == parse_line(lines2[0])


matching_files = glob.glob("./yours/*.debug")

pass_all = True
print("===== Start Tests =====")
for file in matching_files:
    correct_file = os.path.join("./correct", os.path.basename(file))
    if compare_files(file, correct_file):
        print("== passed {} ==".format(file.split("/")[2]))
    else:
        pass_all = False
        print("!! failed {} !!".format(file.split("/")[2]))

if pass_all:
    print("===== Passed All Tests =====")
else:
    print("!!!!! Some Tests Failed !!!!!")
