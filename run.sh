#!/bin/sh
# NDSU Byte-le 2026 Submission Script
# SPDX-License-Identifier: MIT
# Copyright (c): 2026, The Scout from Team Fortress 2

PROJECT_FOLDER="./fivenights"
set -e

main() {
    # shellcheck disable=SC1091
    . "${PROJECT_FOLDER}/.venv/bin/activate"
    cd "$PROJECT_FOLDER"
    clear
    set -e
    python launcher.pyz client leaderboard -include_alumni && printf "\n"
    # python launcher.pyz --help && printf "\n" # Li'l help pushin' the cart?
    python launcher.pyz grv || exit
    printf "\n"
    python launcher.pyz client submit
}

# shellcheck disable=SC2068
main $@
