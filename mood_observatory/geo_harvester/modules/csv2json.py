import csv
import json
import sys

# quick and dirty, here as a reminder of what I need to do! :)
print(json.dumps(list(csv.reader(open(sys.argv[1])))))

# needs making pretty and file management
