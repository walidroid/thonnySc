# PyInstaller hook to filter friendly_traceback locales
# Keep only French locale, remove all others

from PyInstaller.utils.hooks import collect_data_files

# Collect all friendly_traceback data files
datas = collect_data_files('friendly_traceback')

# Filter to keep only French locales
filtered_datas = []
for src, dest in datas:
    # Keep only French locale files (+ base files)
    if ('locales\\\\fr' in src or 'locales/fr' in src or 
        'friendly_tb.pot' in src or 
        'py.typed' in src):
        filtered_datas.append((src, dest))

# Replace with filtered list
datas = filtered_datas
