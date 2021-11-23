import subprocess
import sys, requests, json, argparse
import os, time, shutil, time
import uuid, datetime
from constants import *
from pipeline import Pipeline

def main():
    # Args details
    _p = argparse.ArgumentParser(description='Pipeline options')
    _p.add_argument('-v', dest='video_path', help='Video to be tested')
    _p.add_argument('-t', dest='target', default="all", help='Target plate')
    # _p.add_argument('-m', dest='mode', default="auto", help='Operation mode (auto/manual/benchmark) default: auto')
    
    # Get args
    args = _p.parse_args()

    # Initialize Pipeline object
    print("===============================================")
    print(PROJECT_NAME, f"({PROJECT_VERSION})", "starting...")
    print("===============================================")

    execute_pipeline(args.video_path, args.target)

    # End of program
    print("===============================================")
    print(PROJECT_NAME, f"({PROJECT_VERSION})", "finished.")
    print("===============================================")

def execute_pipeline(video_path, target):
    print("===============================================")
    print(f"Executing pipeline for {video_path}:")
    pline = Pipeline(video_path);

    start = time.time()
    pline.capture_video(15) # Capture at 15 fps
    pline.get_target(target)
    end = time.time()
    print(f"Pipeline completed with {end-start}s")
    print("===============================================")

if __name__ == "__main__":
    main()