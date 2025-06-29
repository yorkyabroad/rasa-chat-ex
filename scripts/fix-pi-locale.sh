#!/bin/bash

# Fix locale warnings on Raspberry Pi

echo "Fixing locale settings..."

# Generate the locale
sudo locale-gen en_GB.UTF-8

# Set environment variables
echo "export LC_ALL=en_GB.UTF-8" >> ~/.bashrc
echo "export LANG=en_GB.UTF-8" >> ~/.bashrc

# Apply immediately
export LC_ALL=en_GB.UTF-8
export LANG=en_GB.UTF-8

echo "Locale fixed. Restart your terminal or run:"
echo "source ~/.bashrc"