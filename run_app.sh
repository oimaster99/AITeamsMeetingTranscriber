#!/bin/bash
cd "$(dirname "$0")"
source .venv-pythonorg/bin/activate 2>/dev/null || true
export QT_QPA_PLATFORM_PLUGIN_PATH="$(python -c 'from PyQt5.QtCore import QLibraryInfo; print(QLibraryInfo.location(QLibraryInfo.PluginsPath) + "/platforms")' 2>/dev/null)"
python AITeamsMeetingTranscriber_GUI_v1.0.py
