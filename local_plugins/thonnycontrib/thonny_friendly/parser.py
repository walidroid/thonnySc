from friendly_traceback.typing_info import InclusionChoice, Info
def parseable(info: Info, include: InclusionChoice = "friendly_tb") -> str:
    """Formatter that separates different parts of the error message for easy parsing."""
    sections = []

    if "header" in info:
        sections.append(f"Header: {info['header']}")

    if "message" in info:
        sections.append(f"Message: {info['message']}")

    if "original_python_traceback" in info:
        sections.append("Original Python Traceback:")
        sections.append(info['original_python_traceback'])

    if "simulated_python_traceback" in info:
        sections.append("Simulated Python Traceback:")
        sections.append(info['simulated_python_traceback'])

    if "shortened_traceback" in info:
        sections.append("Shortened Traceback:")
        sections.append(info['shortened_traceback'])

    if "exception_notes_intro" in info:
        sections.append("Exception Notes Intro:")
        sections.extend(info['exception_notes_intro'])

    if "exception_notes" in info:
        sections.append("Exception Notes:")
        sections.append(info['exception_notes'])

    if "suggest" in info:
        sections.append("Suggestion:")
        sections.append(info['suggest'])

    if "generic" in info:
        sections.append("Generic:")
        sections.append(info['generic'])

    if "parsing_error" in info:
        sections.append("Parsing Error:")
        sections.append(info['parsing_error'])

    if "parsing_error_source" in info:
        sections.append("Parsing Error Source:")
        sections.append(info['parsing_error_source'])

    if "cause" in info:
        sections.append("Cause:")
        sections.append(info['cause'])

    if "detailed_tb" in info:
        sections.append("Detailed Traceback:")
        sections.extend(info['detailed_tb'])

    if "last_call_header" in info:
        sections.append("Last Call Header:")
        sections.append(info['last_call_header'])

    if "last_call_source" in info:
        sections.append("Last Call Source:")
        sections.append(info['last_call_source'])

    if "last_call_variables" in info:
        sections.append("Last Call Variables:")
        sections.append(info['last_call_variables'])

    if "exception_raised_header" in info:
        sections.append("Exception Raised Header:")
        sections.append(info['exception_raised_header'])

    if "exception_raised_source" in info:
        sections.append("Exception Raised Source:")
        sections.append(info['exception_raised_source'])

    if "exception_raised_variables" in info:
        sections.append("Exception Raised Variables:")
        sections.append(info['exception_raised_variables'])

    if "warning_message" in info:
        sections.append("Warning Message:")
        sections.append(info['warning_message'])

    if "warning_location_header" in info:
        sections.append("Warning Location Header:")
        sections.append(info['warning_location_header'])

    if "warning_source" in info:
        sections.append("Warning Source:")
        sections.append(info['warning_source'])

    if "warning_variables" in info:
        sections.append("Warning Variables:")
        sections.append(info['warning_variables'])

    if "additional_variable_warning" in info:
        sections.append("Additional Variable Warning:")
        sections.append(info['additional_variable_warning'])

    if "lang" in info:
        sections.append(f"Language: {info['lang']}")

    if "_tb_data" in info:
        sections.append("Traceback Data:")
        sections.append(str(info['_tb_data']))

    #print(sections)
    #return""
    #@TODO: make this better
    return '\n'.join(str(item) for item in sections)
