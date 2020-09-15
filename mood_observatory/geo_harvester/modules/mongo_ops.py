import os
import subprocess
from subprocess import CalledProcessError
import sys
import time
import psutil
import pymongo


def mongo_checks():

    """figure out where mongodb executables are on this system,
    assign them to variables"""

    try:
        mongod_executable_path = (
            subprocess.check_output(["which", "mongod"]).decode("utf-8").strip()
        )
    except CalledProcessError:
        print(f"You don't seem to have MongoDB installed. Stopping.")
        sys.exit()

    try:
        mongoexport_executable_path = (
            subprocess.check_output(["which", "mongoexport"]).decode("utf-8").strip()
        )
    except CalledProcessError:
        print(f"Mongoexport seems missing... stopping.")
        sys.exit()

    try:
        mongodump_executable_path = (
            subprocess.check_output(["which", "mongodump"]).decode("utf-8").strip()
        )
    except CalledProcessError:
        print(f"Mongodump seems missing... stopping.")
        sys.exit()

    try:
        mongoimport_executable_path = (
            subprocess.check_output(["which", "mongoimport"]).decode("utf-8").strip()
        )
    except CalledProcessError:
        print(f"Mongoimport seems missing... stopping.")
        sys.exit()

    return (
        mongod_executable_path,
        mongoexport_executable_path,
        mongodump_executable_path,
        mongoimport_executable_path,
    )


def start_mongo(mongod_executable_path, db_path, db_log_filename):

    """start mongo daemon, unless it is already running"""

    def mongo_go():
        print(f"\nStarting the MongoDB daemon...\n")
        try:
            subprocess.Popen(
                [
                    mongod_executable_path,
                    "--dbpath",
                    db_path,
                    "--logpath",
                    db_log_filename,
                ]
            )
            time.sleep(1)
        except subprocess.CalledProcessError as e:
            print(
                f"There is a problem opening the MonogoDB daemon... halting.\n",
                e.output,
            )
            sys.exit()

    try:
        if "mongod" in (p.name() for p in psutil.process_iter()):
            print(
                f"\nMongoDB daemon appears to be already running. This could cause conflicts. Please stop the daemon and retry."
            )
            print(f"(You can do this with the command: pkill -15 mongod)\n")
            sys.exit()
        else:
            mongo_go()
    except psutil.ZombieProcess:
        mongo_go()


def stop_mongo():

    """gracefully close the mongo daemon"""

    client = pymongo.MongoClient("localhost", 27017)
    print(f"\nAsking MongoDB to close...")
    client.close()
    subprocess.call(["pkill", "-15", "mongod"])
    timeout = 60
    while timeout > 0:
        try:
            subprocess.check_output(["pgrep", "mongod"])
        except subprocess.CalledProcessError:
            print(f"\nOK, MongoDB daemon closed.")
            break
        if "--log" not in sys.argv:
            print(".", end="", flush=True)
        time.sleep(1)
        timeout -= 1
    if timeout == 0:
        print(
            f"\nMongoDB didn't respond to requests to close... be aware that MongoDB is still running."
        )


def index_mongo(run_folder):

    """tidy up the database so that upsert operations are faster"""

    client = pymongo.MongoClient("localhost", 27017)
    db = client.twitter_db
    if not os.path.isfile(run_folder + "/db/WiredTiger"):
        return
    print(f"\nIndexing MongoDB...")
    db.tweets.create_index([("id_str", pymongo.ASCENDING)], unique=True, dropDups=True)


def export_and_backup(
    mongoexport_executable_path,
    mongodump_executable_path,
    database_dump_path,
    csv_filename,
):

    """Export some fields from the tweets in MongoDB into a CSV file
    then backup and compress the database"""

    print(f"\nCreating CSV output file...")
    subprocess.call(
        [
            mongoexport_executable_path,
            "--host=127.0.0.1",
            "--db",
            "twitter_db",
            "--collection",
            "tweets",
            "--type=csv",
            "--out",
            csv_filename,
            "--fields",
            "user.id_str,id_str,created_at,full_text,retweeted_status.full_text",
        ]
    )
    print(f"\nBacking up the database...")
    subprocess.call(
        [mongodump_executable_path, "-o", database_dump_path, "--host=127.0.0.1"]
    )
    subprocess.call(
        ["chmod", "-R", "0755", database_dump_path]
    )  # hand back access permissions to host


def export_latest_tweet(mongoexport_executable_path):

    """Export most recent tweet as csv"""

    print(f"\nCreating CSV output file...")
    subprocess.call(
        [
            mongoexport_executable_path,
            "--host=127.0.0.1",
            "--db=geotweets",
            "--collection=geotweets_collection",
            "--type=csv",
            "--out=latest_geotweet.csv",
            "--fields=created_at,geo.coordinates,text",
            '--sort="{_id:-1}"',
            "--limit=1",
        ]
    )


def import_analysed_tweet(mongoimport_executable_path, latest_tweet):

    """Import metrics from sentiment analysis into MongoDB"""

    print(f"\nImporting LIWC analysis output...")
    subprocess.call(
        [
            mongoimport_executable_path,
            "--host=127.0.0.1",
            "--db=geotweets",
            "--collection=geotweets_analysed",
            "--type=csv",
            "--headerline",
            "--file=" + latest_tweet,
        ]
    )
