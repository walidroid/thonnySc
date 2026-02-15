import os
import sys

if getattr(sys, 'frozen', False):
    # Running as bundled exe
    bundle_dir = sys._MEIPASS
    os.environ['QT_PLUGIN_PATH'] = os.path.join(bundle_dir, 'PyQt5', 'Qt5', 'plugins')
    # Suppress Qt warnings that might cause crashes
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

from thonny import launch, report_time

report_time("Before launch")
launch()
