# filename: my_script.py
import sys

# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    print("Usage: python code.py test_data.csv")
    sys.exit(1)

# Retrieve arguments
arg1 = sys.argv[1]

# Your code here using arg1 and arg2
print(f"Argument 1: {arg1}")
