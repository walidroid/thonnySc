=========
ThonnySc
=========

**A Powerful Python IDE for Beginners with Integrated Qt Designer**

.. image:: https://img.shields.io/badge/Python-3.11%2B-blue.svg
   :target: https://www.python.org/downloads/
.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :target: LICENSE.txt
.. image:: https://img.shields.io/badge/Platform-Windows-lightgrey.svg

Overview
--------

ThonnySc is an enhanced fork of `Thonny <https://thonny.org>`_, the beginner-friendly Python IDE. 
It extends the original Thonny with powerful GUI development capabilities by integrating 
**Qt Designer** directly into the development environment, enabling students and educators to 
create modern graphical user interfaces alongside their Python code.

Key Features
------------

🎨 **Integrated Qt Designer**
   Design professional GUI applications with drag-and-drop interface builder. 
   Create ``.ui`` files and load them seamlessly with PyQt5.

🐍 **Beginner-Friendly Python Development**
   Step-through debugger, variable explorer, and syntax highlighting designed 
   specifically for learners.

🔌 **ESP32/ESP8266 Support**
   Built-in esptool integration for MicroPython development on embedded devices.

📝 **Intelligent Code Assistance**
   - Syntax checking with Ruff
   - Type checking with MyPy
   - Code linting with Pylint
   - Auto-completion support

🌍 **Multi-Language Support**
   Full French and English localization for international classrooms.

💾 **Offline-Ready**
   Complete standalone installation with all dependencies bundled. 
   No internet connection required after installation.

🔧 **Extensible Plugin System**
   - Auto-save functionality
   - Quick file switching
   - Error translation
   - Custom themes

Installation
------------

**Windows Installer (Recommended)**

1. Download the latest installer from `Releases <https://github.com/walidroid/thonnySc/releases>`_
2. Run the installer and follow the prompts
3. Launch ThonnySc from the desktop shortcut

**From Source**

.. code-block:: bash

   git clone https://github.com/walidroid/thonnySc.git
   cd thonnySc
   pip install -r requirements.txt
   python -m thonny

Building the Installer
----------------------

To build the Windows installer locally:

.. code-block:: powershell

   # Requires: Python 3.11+, Inno Setup 6
   .\build.ps1 -Version "1.0.0"

The installer will be created in the ``output/`` directory.

Project Structure
-----------------

.. code-block:: text

   thonnySc/
   ├── thonny/              # Core IDE source code
   ├── local_plugins/       # Bundled plugins
   ├── Qt Designer/         # Standalone Qt Designer
   ├── Python/              # Embedded Python distribution
   ├── build.ps1            # Local build script
   ├── thonny.spec          # PyInstaller configuration
   └── installer.iss        # Inno Setup installer script

Requirements
------------

- Python 3.11 or higher
- Windows 10/11 (64-bit)
- For building: Inno Setup 6, PyInstaller

License
-------

This project is licensed under the MIT License. See `LICENSE.txt <LICENSE.txt>`_ for details.

ThonnySc is based on `Thonny <https://github.com/thonny/thonny>`_ by Aivar Annamaa 
and contributors.

Contributing
------------

Contributions are welcome! Please feel free to submit issues and pull requests.

1. Fork the repository
2. Create a feature branch (``git checkout -b feature/amazing-feature``)
3. Commit your changes (``git commit -m 'Add amazing feature'``)
4. Push to the branch (``git push origin feature/amazing-feature``)
5. Open a Pull Request

Acknowledgments
---------------

- `Thonny <https://thonny.org>`_ - The original beginner-friendly Python IDE
- `Qt Designer <https://doc.qt.io/qt-5/qtdesigner-manual.html>`_ - GUI design tool
- `PyQt5 <https://www.riverbankcomputing.com/software/pyqt/>`_ - Python bindings for Qt

---

*Made with ❤️ for educators and students worldwide*
