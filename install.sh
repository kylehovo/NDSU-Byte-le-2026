#!/bin/sh
# NDSU Byte-le 2026 Installation Script
# SPDX-License-Identifier: MIT
# Copyright (c): 2026, The Scout from Team Fortress 2
# Based on the official documentation: https://ndacm.org/Byte-le-Engine-v2-2026/getting_started.html
# Meant for Debian-based distros only

PYTHON_VERSION="3.13"
PROJECT_FOLDER="./fivenights"
PREVIOUS_PROJECT_FOLDER="${PROJECT_FOLDER}-prev"
URL="https://github.com/acm-ndsu/Byte-le-2026-Client-Package/archive/refs/heads/main.zip"

dep() {
    if ! command -v "$1" 2>/dev/null 1>/dev/null; then
        echo "Error: $1 does not exist" 1>&2
        exit 127
    fi
}

main() {
    set -ex

    dep apt
    dep sudo
    sudo apt install -y curl make pipx python3 sudo tar unzip
    pipx install uv # uv is way better than pip

    [ -d "$PREVIOUS_PROJECT_FOLDER" ] && rm -rf "$PREVIOUS_PROJECT_FOLDER"
    [ -d "$PROJECT_FOLDER" ] && mv -v "$PROJECT_FOLDER" "$PREVIOUS_PROJECT_FOLDER"

    # Download Byte-le Client
    curl "$URL" -L -o tmp.zip
    unzip tmp.zip && rm tmp.zip
    mv "Byte-le-2026-Client-Package-main" "$PROJECT_FOLDER"
    [ -f "vID" ] && cp -v "vID" "${PROJECT_FOLDER}/vID"
    [ -f "$PREVIOUS_PROJECT_FOLDER/base_client.py" ] && cp -v "$PREVIOUS_PROJECT_FOLDER/base_client.py" "$PROJECT_FOLDER/base_client.py"
    cd "$PROJECT_FOLDER"

    # Set up Python environment
    [ -f "pyproject.toml" ] || uv init .
    uv python install "$PYTHON_VERSION"
    uv venv --python "$PYTHON_VERSION" --clear
    # shellcheck disable=SC1091
    . ./.venv/bin/activate
    uv python pin "$PYTHON_VERSION"
    uv add -r requirements.txt

    set +x
    printf "\n"
    echo "Run '. ${PROJECT_FOLDER}/.venv/bin/activate' to activate the virtual environment" 
    echo "Run 'python launcher.pyz --help' for help"
    if ! [ -f "vID" ]; then
		echo "Run 'python launcher.pyz client register' to register"
		echo "DO NOT SHARE YOUR vID. THE ANIMATRONICS WILL GET YOU." # and they are known to get a little quirky at night...
	fi
}

# shellcheck disable=SC2068
main $@
