# Importamos las bibliotecas necesarias
import os
import re
import logging as log
import datetime
from utils.string_mapping import MAPPING

# -- Configuration ---
INPUT_DIRECTORY = "./files/"
CATALOG_DIRECTORY = f"{INPUT_DIRECTORY}catalogs/"
LOGS_DIRECTORY = "./logs/"

OUTPUT_DIRECTORY = f"{INPUT_DIRECTORY}cleaned/"
ROOT = "https://acordes.lacuerda.net"
URL_ARTIST_INDEX = "https://acordes.lacuerda.net/tabs/"
MIN_LINES = 5
SONG_VERSION = 0
INDEX = "abcdefghijklmnopqrstuvwxyz#"

dir_list = list()

# --- Logging config---
logger = log.getLogger(__name__)

log.basicConfig(
    filename=f"{LOGS_DIRECTORY}cleaner.log",
    filemode="w",
    encoding="utf-8",
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=log.INFO,
)

# --- Logic---


def list_files_recursive(path="."):

    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            list_files_recursive(full_path)
        else:
            dir_list.append(full_path)

    return dir_list


def remove_email_sentences(text: str):

    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    sentence_pattern = r"[\n^.!?]*" + email_pattern + r"[^.!?]*[.!?\n]"

    return re.sub(sentence_pattern, "", text)


def apply_format_rules(text: str):
    formatted_text = str

    formatted_text = remove_email_sentences(text)

    for key, value in MAPPING.items():
        formatted_text = re.sub(
            key, value, formatted_text, flags=re.DOTALL & re.IGNORECASE
        )
    return formatted_text


def main():

    # Start time tracking
    start_time = datetime.datetime.now()
    log.info(f"Cleaner started at {start_time}")
    print("Starting cleaner...")

    cleaned = 0

    for file_path in list_files_recursive(INPUT_DIRECTORY):
        log.info(f"Processing files... -> {file_path}")
        text = str()
        with open(file_path, "r") as file:
            text = file.read()
        if text.count("\n") < MIN_LINES:
            log.info("Empty or too small tab. Skipping.............................")
            continue
        # Formatting of the text goes in that function call

        formatted_text = apply_format_rules(text)

        output_file = file_path.replace(INPUT_DIRECTORY, OUTPUT_DIRECTORY)
        dir = "/".join(output_file.split("/")[:-1])
        file_name = output_file.split("/")[-1:]

        # Creates the path if not exists
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
            print("INFO", dir, " CREATED!!")

        cleaned += 1
        with open(output_file, "w") as file:
            file.write(formatted_text)
            print(cleaned, "--", file_name, " CREATED!!")

    end_time = datetime.datetime.now()
    log.info(f"Cleaner ended at {end_time}")
    duration = end_time - start_time
    log.info(f"Total duration: {duration}")
    print(
        f"Cleaner finished. Duration in seconds: {duration.total_seconds()}, that is {duration.total_seconds() / 60} minutes."
    )


if __name__ == "__main__":
    main()
