#!/bin/bash

set -e

echo "Cleaning old builds..."
rm -rf build dist *.spec

echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

echo "Building executable..."
pyinstaller --onefile --windowed app.py

echo "Creating release zip..."
mkdir -p release
cp dist/app.exe release/
cd release
zip -r SpartanGroupBuilder.zip app.exe
cd ..

echo "Committing source changes..."
git add .
git commit -m "Release build $(date +%Y-%m-%d_%H-%M-%S)" || true

echo "Pushing to GitHub..."
git push

echo ""
echo "Build complete."
echo "ZIP location:"
echo "release/SpartanGroupBuilder.zip"