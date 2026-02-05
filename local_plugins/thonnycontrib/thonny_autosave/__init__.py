import sched, time
from thonny import get_workbench
from thonny.languages import tr
from logging import getLogger

get_workbench().set_default("general.autosave",True)
logger = getLogger(__name__)
logger.setLevel(51)

#logger.exception("dddddd")

def toggle_autosave():
    if get_workbench().get_option("general.autosave")==False:
        get_workbench().set_option("general.autosave",True)
    else:
        get_workbench().set_option("general.autosave",False)



def save_all(): 
    # logger.info("entering save_all")
    get_workbench().after(10000, save_all)
    
    if get_workbench().get_option("general.autosave"):
        try:
            editor_notebook = get_workbench().get_editor_notebook()
            # Iterate over all editors
            for editor in editor_notebook.get_all_editors():
                filename = editor.get_filename(False)
                if filename and editor.is_modified():
                    logger.info(f"Autosaving {filename}")
                    editor.save_file()
        except Exception as e:
            logger.error(f"Error in autosave: {e}")

def load_plugin():
    get_workbench().add_command(
        "toggle_autosave",
        "file",
        tr("Autosave"),
        flag_name="general.autosave",
        handler=toggle_autosave
    )
    print("DEBUG: thonny_autosave.load_plugin called")
    logger.info("Starting autosave loop")
    save_all()

print("DEBUG: thonny_autosave module imported")
