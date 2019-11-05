import subprocess
import sys

def check_mongo():

    """check if MongoDB is present and correct"""

    print(f"Verifying MongoDB...")
    try:
        mongod_executable_path = subprocess.check_output(['which', 'mongod']).decode('utf-8').strip()
    except:
        print(f"You don't seem to have MongoDB installed. Stopping.")
        sys.exit()
    try:
        mongoexport_executable_path = subprocess.check_output(['which', 'mongoexport']).decode('utf-8').strip()
    except:
        print(f"Mongoexport seems missing... stopping.")
        sys.exit()
    try:
        mongodump_executable_path = subprocess.check_output(['which', 'mongodump']).decode('utf-8').strip()
    except:
        print(f"Mongodump seems missing... stopping.")
        sys.exit()
    print(f"OK, MongoDB present and correct.")
    return mongod_executable_path, mongoexport_executable_path, mongodump_executable_path

