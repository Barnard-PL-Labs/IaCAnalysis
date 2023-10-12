import argparse
import json
import z3



def read_cf_json(fpath):
    with open(fpath, "r") as f:
        return json.load(f)

def main():
   # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="IaC analysis")

    # Add command-line arguments
    parser.add_argument("-f", "--file", help="Path to a CloudFormation template")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values of the arguments
    if args.file:
        print(read_cf_json(args.file))

if __name__ == "__main__":
    main()