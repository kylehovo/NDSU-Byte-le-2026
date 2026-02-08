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
    while true; do
        clear
        echo "Watch live: https://www.twitch.tv/ndsu_acm"
        python launcher.pyz client leaderboard -include_alumni
        sleep 15
    done
}

# shellcheck disable=SC2068
main $@
