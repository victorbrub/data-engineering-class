import datetime
import click
import logging as log
import utils.files as files
import utils.songs as songs

# -- Configuration ---
OUTPUT_DIRECTORY = (
    "./files/"
)
SONGS_DIRECTORY = f"{OUTPUT_DIRECTORY}songs/"
CATALOG_DIRECTORY = f"{OUTPUT_DIRECTORY}catalogs/"
LOGS_DIRECTORY = "./logs/"
ROOT = "https://acordes.lacuerda.net"
URL_ARTIST_INDEX = f"{ROOT}/tabs/"
SONG_VERSION = None
INDEX = "abcdefghijklmnopqrstuvwxyz"

# --- Logging config---
logger = log.getLogger(__name__)

log.basicConfig(
    filename=f"{LOGS_DIRECTORY}scrapper.log",
    filemode="w",
    encoding="utf-8",
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=log.INFO,
)


# --- Logic---


@click.command()
@click.option(
    "-r",
    "--reset",
    is_flag=True,
    default=False,
    help="Delete the existing data and start fresh.",
)
@click.option(
    "-uc",
    "--update_catalog",
    is_flag=True,
    default=False,
    help="Regenerates the catalogs.",
)
@click.option("--start_char", "-sc", default="a", help="Starting letter for artists.")
@click.option("--end_char", "-ec", default="z", help="Ending letter for artists.")
@click.option("--artist", "-a", default=None, help="Specific artist to process.")
def main(reset, update_catalog, start_char, end_char, artist):

    # Start time tracking
    start_time = datetime.datetime.now()
    log.info(f"Scrapper started at {start_time}")
    print("Starting scrapper...")

    if reset:
        files.delete(OUTPUT_DIRECTORY)
        log.info("Fresh start...")

    if update_catalog:
        files.delete(CATALOG_DIRECTORY)
        catalog = songs.get_catalog(
            SONGS_DIRECTORY,
            catalog_level="songs",
            start_char=start_char,
            end_char=end_char,
            selected_artist=artist,
        )

        # Save Artist Catalog
        print("Updating artist catalog.")
        files.save_to_json(
            [x.to_dict_no_songs() for x in catalog],
            CATALOG_DIRECTORY,
            "artist_catalog.json",
        )

        # Save Full Catalog
        print("Updating json catalog.")
        files.save_to_json(catalog, CATALOG_DIRECTORY, "catalog.json")

    # Get songs lyrics
    log.info("Starting to download lyrics...")
    songs.get_songs(SONGS_DIRECTORY, version=SONG_VERSION)

    end_time = datetime.datetime.now()
    log.info(f"Scrapper ended at {end_time}")
    duration = end_time - start_time
    log.info(f"Total duration: {duration}")
    print(
        f"Scrapper finished. Duration in seconds: {duration.total_seconds()}, that is {duration.total_seconds() / 60} minutes."
    )


if __name__ == "__main__":
    main()
