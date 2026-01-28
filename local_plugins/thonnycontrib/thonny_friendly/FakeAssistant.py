import os
from thonny import  get_workbench, rst_utils
from thonny.assistance import AssistantView
class FakeAssistant:
    def custom_present_warnings(self):
        warnings = [w for ws in self._accepted_warning_sets for w in ws]
        self.text.direct_delete("end-2l linestart", "end-1c lineend")

        if not warnings:
            return

        if self._exception_info is None:
            intro = "Pas d'erreur critique détectée. Vous pouvez améliorer le code si nécessaire."
        else:
            intro = "Cette explication peut vous aider à comprendre la cause de l'erreur."

        rst = rst_utils.create_title("Messages explicatifs :") + ":remark:`%s`\n\n" % intro
        # Then continue formatting the warnings as before...

        by_file = {}
        for warning in warnings:
            if warning["filename"] not in by_file:
                by_file[warning["filename"]] = []
            if warning not in by_file[warning["filename"]]:
                # Pylint may give double warnings (eg. when module imports itself)
                by_file[warning["filename"]].append(warning)

        for filename in by_file:
            rst += "`%s <%s>`__\n\n" % (
                os.path.basename(filename),
                self._format_file_url(dict(filename=filename)),
            )
            file_warnings = sorted(
                by_file[filename], key=lambda x: (x.get("lineno", 0), -x.get("relevance", 1))
            )

            for i, warning in enumerate(file_warnings):
                rst += self._format_warning(warning, i == len(file_warnings) - 1) + "\n"

            rst += "\n"

        self.text.append_rst(rst)

        # save snapshot
        self._current_snapshot["warnings_rst"] = rst
        self._current_snapshot["warnings"] = warnings

        if get_workbench().get_option("assistance.open_assistant_on_warnings"):
            get_workbench().show_view("AssistantView")
        

    def custom_format_warning(self, warning, last):
        return AssistantView.old_format_warning(self,warning, last).replace("toggle", "toggle open")