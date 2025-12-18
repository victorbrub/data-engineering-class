#!/bin/bash

# Script to remove all Zone.Identifier files recursively

echo "Searching for Zone.Identifier files..."

# Find and remove all files containing :Zone.Identifier
find . -name "*:Zone.Identifier*" -type f -print -delete

echo "All Zone.Identifier files have been removed."
