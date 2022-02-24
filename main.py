# Sample code from Google for reading the input

# input() reads a string with a line of input, stripping the ' ' (newline) at the end.
# Note that you have to set the input file in the Pycharm "Redirect input from" or use main.py < input.txt

# This is all you need for most problems.
num_test_cases = int(input())  # read a line with a single integer
for test_case_num in range(1, num_test_cases + 1):
    n, m = [int(s) for s in input().split(" ")]  # read a list of integers, 2 in this case
    print(f"Case #{test_case_num}: {n+m} {n*m}")
