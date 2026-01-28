from thonny.languages import tr

import re
from logging import getLogger
from typing import Iterable
from thonny import  get_workbench
from thonny.program_analysis import ProgramAnalyzer
from thonny.assistance import AssistantView, add_program_analyzer,add_error_helper
from thonny.config_ui import ConfigurationPage

from .parser import parseable
from .GenericErrorHelper import GenericErrorHelper
from .FakeAssistant import FakeAssistant


logger = getLogger(__name__)




class FriendlyAnalyzer(ProgramAnalyzer):
    def is_enabled(self):
        return get_workbench().get_option("assistance.use_friendly")

    def start_analysis(self, main_file_path, imported_file_paths: Iterable[str]) -> None:
        
        self.interesting_files = [main_file_path] + list(imported_file_paths) +[get_workbench().get_local_cwd()]
        import friendly_traceback
        #print("------------------------Start--------------------")
        friendly_traceback.run(main_file_path,include="friendly_tb",console=False,redirect="capture",formatter=parseable,lang="fr")
        #print("explain tracebackX : ")
        x= friendly_traceback.get_output()
        #print("x= " , x)
        self._parse_and_output_warnings(None, x, None)
        #assistance._explain_exception()

        #print("------------------------END--------------------")


        """"
        args = [
            get_front_interpreter_for_subprocess(),
            "-m",
            "friendly_traceback",
            "--formatter",
            "thonnycontrib.thonny_friendly.parser.parseable",
            "--lang",
            "fr",
#            "--ignore-missing-imports",
#            "--check-untyped-defs",
#            "--warn-redundant-casts",
#            "--warn-unused-ignores",
#            "--show-column-numbers",
            main_file_path,
        ] + list(imported_file_paths)

        logger.debug("Running friendly: %s", " ".join(args))

        # TODO: ignore "... need type annotation" messages
"""

    def _parse_and_output_warnings(self, pylint_proc, out_lines, err_lines):


        infos={}
        warnings=[]
        file_name = None
        line_number = None
        for line in  out_lines.split('\n\n'):
            atts = {
                "filename": file_name,
                "explanation": None,
                "lineno": line_number,
                "kind": "warning",
                "title": "Warning",
                "msg": "Warning",
                "group": "0",
                "col_offset": 0,
                "symbol": "friendly-warning"
            }
            if "Simulated Python Traceback:" in line:
                match = re.search(r'File "(.*?)", line (\d+)', line)
                if match:
                    file_name = match.group(1)
                    line_number = int(match.group(2))
                    atts['filename'] = file_name
                    atts['lineno'] = line_number
                    infos['filename'] = file_name
                    infos['lineno'] = line_number

                atts['explanation'] = line.split(':', 1)[1].strip()
                atts['msg'] = "Simulated Python Traceback"
                #warnings.append(atts.copy())
            elif "Shortened Traceback:" in line:
                atts['explanation'] = line.split(':', 1)[1].strip()
                atts['msg'] = "Shortened Traceback"
                #warnings.append(atts.copy())
            elif "Suggestion:" in line:
                atts['explanation'] = line.split(':', 1)[1].strip()
                atts['msg'] = "Suggestion :"
                warnings.append(atts.copy())
            elif "Generic:" in line:
                atts['explanation'] = line.split(':', 1)[1].strip()
                atts['msg'] = "Explication :"
                warnings.append(atts.copy())
            elif "Cause :" in line:
                atts['explanation'] = line.split(':', 1)[1].strip()
                atts['msg'] = "Cause :"
                warnings.append(atts.copy())
            elif "Exception Raised Header:" in line:
                atts['explanation'] = line.split(':', 1)[1].strip()
                atts['msg'] = "Exception Raised Header"
                #warnings.append(atts.copy())
        

        self.completion_handler(self, warnings)

class FriendlyConfigPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        self.add_checkbox("assistance.use_friendly","Friendly", row=4, columnspan=2,tooltip="Afficher les suggestions Friendly")


def load_plugin():
    import friendly_traceback
    friendly_traceback.install(lang="fr")
    AssistantView._present_warnings = FakeAssistant.custom_present_warnings
    AssistantView.old_format_warning = AssistantView._format_warning
    AssistantView._format_warning = FakeAssistant.custom_format_warning
    add_program_analyzer(FriendlyAnalyzer)
    get_workbench().set_default("assistance.use_friendly", True)
    get_workbench().add_configuration_page("friendly", tr("Friendly"), FriendlyConfigPage, 90)
    add_error_helper("*", GenericErrorHelper)
