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
    _p.add_argument('-m', dest='mode', default="auto", help='Operation mode (auto/manual/benchmark) default: auto')
    
    # Get args
    args = _p.parse_args()

    # Initialize Pipeline object
    print("===============================================")
    print(PROJECT_NAME, f"({PROJECT_VERSION})", "starting...")
    print("===============================================")

    if args.mode == "manual":
        execute_pipeline(args.video_path, args.target)

    elif args.mode == "auto":
        print(f"Checking for directory changes every {CHECK_INTERVAL} seconds...")
        video_in = ','.join(sorted(os.listdir(f"{os.getcwd()}/{VIDEO_DIR}")))
        while True:
            time.sleep(CHECK_INTERVAL)
            new_videos = sorted(os.listdir(f"{os.getcwd()}/{VIDEO_DIR}"))
            video_in_new = ','.join(new_videos)
            if (video_in != video_in_new):
                for video in new_videos:
                    if not video.endswith(".mp4"): continue
                    video_path = f"{VIDEO_DIR}/{video}"
                    video_path_abs = f"{os.getcwd()}/{video_path}"

                    execute_pipeline(video_path, args.target)
                    os.remove(video_path_abs)

    elif args.mode == "benchmark":
        for i in range(1, 6):
            execute_pipeline(f"test_videos/test_video_{i}.mp4", "all")

    # End of program
    print("===============================================")
    print(PROJECT_NAME, f"({PROJECT_VERSION})", "finished.")
    print("===============================================")

def execute_pipeline(video_path, target):
    print("===============================================")
    print(f"Executing pipeline for {video_path}:")
    pline = Pipeline(video_path);

    start = time.time()

    pline.capture_video(CAPTURE_FPS)
    pline.get_target(target)

    end = time.time()

    print(f"Pipeline completed with {end-start}s")
    print("===============================================")

if __name__ == "__main__":
    main()