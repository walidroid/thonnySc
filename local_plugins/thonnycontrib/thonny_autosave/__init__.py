from thonny import get_workbench
from thonny.languages import tr
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel(51)


def toggle_autosave():
    wb = get_workbench()
    if wb:
        current = wb.get_option("general.autosave")
        wb.set_option("general.autosave", not current)


def save_all():
    wb = get_workbench()
    if not wb:
        return

    wb.after(10000, save_all)
    
    if wb.get_option("general.autosave"):
        try:
            editor_notebook = wb.get_editor_notebook()
            if editor_notebook:
                for editor in editor_notebook.get_all_editors():
                    filename = editor.get_filename(False)
                    if filename and editor.is_modified():
                        logger.info(f"Autosaving {filename}")
                        editor.save_file()
        except Exception as e:
            logger.error(f"Error in autosave: {e}")


def load_plugin():
    wb = get_workbench()
    wb.set_default("general.autosave", True)
    wb.add_command(
        "toggle_autosave",
        "file",
        tr("Autosave"),
        flag_name="general.autosave",
        handler=toggle_autosave
    )
    logger.info("Starting autosave loop")
    save_all()
