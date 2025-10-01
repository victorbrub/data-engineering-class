import os
import csv
import sys
import logging as log
import json
from pathlib import Path
from attrs import asdict
from typing import Any


def check_file_exists(directory, filename):
    """Checks if a file exists in the specified directory."""
    file_path = os.path.join(directory, filename)
    return os.path.isfile(file_path)


def write_string_to_file(directory, file_name, text):
    """
    Writes a string to a file in the specified directory.
    """
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create the full file path
    file_path = os.path.join(directory, file_name)

    # Write the string to the file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)


def delete(directory: str):
    """Deletes the existing files in the directory.
    If there is a directory, recursive call is made.
    Args:
        directory (str): The directory to delete files from.
    """
    if Path(directory).exists():
        for item in Path(directory).rglob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                delete(item)
        Path(directory).rmdir()
        log.info(f"Deleted existing data directory: {directory}")
    else:
        log.info(f"No existing data directory found at: {directory}")


def save_to_json(
    data: Any,
    file_path: str,
    file_name: str,
    indent: int = 2,
    ensure_ascii: bool = False,
):
    """
    Saves data to a JSON file. Handles various Python objects including dataclasses,
    Path objects, and nested structures.

    Args:
        data (Any): The data to be saved. Can be:
                   - A list of objects (dicts, dataclasses, or objects with .to_dict())
                   - A single object (dict, dataclass, or object with .to_dict())
                   - Any JSON-serializable Python object
        file_path (Path): The full path to the output JSON file.
        indent (int): Number of spaces for JSON indentation (default: 2 for readability).
                     Set to None for compact output.
        ensure_ascii (bool): If True, escapes non-ASCII characters (default: False to preserve Unicode).
    """

    def convert_to_serializable(obj):
        """Recursively converts objects to JSON-serializable format."""

        # Handle Path objects
        if isinstance(obj, Path):
            return str(obj)

        # Handle objects with a to_dict method (like our dataclasses)
        if hasattr(obj, "to_dict") and callable(obj.to_dict):
            return obj.to_dict()

        # Handle dataclasses that might not have to_dict
        if hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)

        # Handle lists and tuples
        if isinstance(obj, (list, tuple)):
            return [convert_to_serializable(item) for item in obj]

        # Handle dictionaries
        if isinstance(obj, dict):
            return {key: convert_to_serializable(value) for key, value in obj.items()}

        # Handle sets (convert to list for JSON)
        if isinstance(obj, set):
            return list(obj)

        # Return as-is for basic types (str, int, float, bool, None)
        return obj

    # Convert the data to a JSON-serializable format
    serializable_data = convert_to_serializable(data)

    file_path = Path(f"{file_path}/{file_name}")

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=indent, ensure_ascii=ensure_ascii)

        # Get file size for informative message
        file_size = file_path.stat().st_size
        if file_size > 1024 * 1024:  # If larger than 1MB
            size_str = f"{file_size / (1024 * 1024):.2f} MB"
        elif file_size > 1024:  # If larger than 1KB
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size} bytes"

        # Count items if it's a list
        if isinstance(serializable_data, list):
            print(
                f"Successfully saved {len(serializable_data)} items to {file_path} ({size_str})"
            )
        else:
            print(f"Successfully saved data to {file_path} ({size_str})")

    except (IOError, OSError) as e:
        print(f"Error saving to {file_path}: {e}", file=sys.stderr)
    except TypeError as e:
        print(f"Data serialization error: {e}", file=sys.stderr)
        print(
            "The data contains objects that cannot be serialized to JSON.",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"An unexpected error occurred while saving to JSON: {e}", file=sys.stderr
        )


def load_from_json(file_path: Path, object_hook=None):
    """
    Loads data from a JSON file.

    Args:
        file_path (Path): The full path to the JSON file to load.
        object_hook (callable, optional): A function that will be called with the result
                                          of every JSON object decoded. Can be used to
                                          convert dicts back to custom objects.

    Returns:
        The loaded data, or None if an error occurred.
    """
    if not file_path.exists():
        print(f"JSON file not found: {file_path}", file=sys.stderr)
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f, object_hook=object_hook)

        # Count items if it's a list
        if isinstance(data, list):
            print(f"Successfully loaded {len(data)} items from {file_path}")
        else:
            print(f"Successfully loaded data from {file_path}")

        return data

    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {file_path}: {e}", file=sys.stderr)
        return None
    except (IOError, OSError) as e:
        print(f"Error reading from {file_path}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading JSON: {e}", file=sys.stderr)
        return None
