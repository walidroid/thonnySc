def load_plugin():
    try:
        import friendly_traceback
        # Install friendly in the backend process to intercept exceptions
        friendly_traceback.install(lang="fr")
        
        # Configure console if needed
        # friendly_traceback.set_console(False) # Keep standard console behavior? Or let friendly take over?
        # friendly.install() replaces sys.excepthook, which affects the console output.
    except ImportError:
        pass
