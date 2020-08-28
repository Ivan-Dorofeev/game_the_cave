import argparse
import sys
from pprint import pprint

parser = argparse.ArgumentParser(description='Ticket to End_Ticket')
parser.add_argument('input_file', type=str, help='Input file for clear Ticket')
parser.add_argument('output_file', type=str, help='Output file for end Ticket')
args = parser.parse_args()
print(args.input_file)