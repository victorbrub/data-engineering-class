## Install dependencies
For installing needed dependencies, run `pip install -r requirements.txt`

## Change the directory names
To change the directory names, you can modify the constants defined in the `main.py` files of each module with your local paths:
- In `scrapper/main.py`, change the `OUTPUT_DIRECTORY` variable.
- In `tab_cleaner/main.py`, change the `INPUT_DIRECTORY` variable.
- In `tab_validator/main.py`, change the `INPUT_DIRECTORY` variable.

## Run the scrapper
To run the scrapper, execute:
```bash
python scrapper/main.py
``` 
This will create a directory `files` with two subdirectories: `songs` and `catalogs`. The `songs` directory will contain the downloaded tabs, and the `catalogs` directory will contain the catalogs of songs.
## Clean the tabs
To clean the downloaded tabs, execute:
```bash
python tab_cleaner/main.py
```
This will create a subdirectory `cleaned` inside the `files` directory, containing the cleaned tabs.

## Validate the cleaned tabs
To validate the cleaned tabs, execute:
```bash
python tab_validator/main.py
```
This will create two subdirectories inside the `files` directory: `validations/ok` and `validations/ko`. The `ok` directory will contain the valid tabs, and the `ko` directory will contain the invalid tabs.