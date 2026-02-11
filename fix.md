OBJECTIVE

✔ Remove vendored serial
✔ Use real pyserial from site-packages
✔ Avoid future shadowing problems
✔ Keep your fork stable

🧠 STEP 1 — Understand Why vendored_libs Exists

vendored_libs in Thonny is used to:

Bundle small dependencies

Avoid installing via pip

Ensure portability

But bundling common libraries like serial is dangerous because:

serial  ← generic name


It will shadow pyserial.

So we remove it safely.

✅ STEP 2 — Remove vendored serial (In Your Source Repo)

Go to your fork repository:

thonny/_internal/thonny/vendored_libs/


Delete:

serial/


Commit the change:

git rm -r thonny/_internal/thonny/vendored_libs/serial
git commit -m "Remove vendored serial to avoid shadowing pyserial"

✅ STEP 3 — Make Sure Nothing Depends on It

Search in your repo:

import serial


Check if any file expects the vendored version specifically.

If they just use:

import serial


You're safe.

If they use relative imports inside vendored folder like:

from .serial import ...


Then adjust accordingly.

But in most cases, you’re safe.

✅ STEP 4 — Install Real pyserial in Embedded Python

Run:

C:\Users\Admin\AppData\Local\Programs\ThonnySc\Python\python.exe -m pip install pyserial


Verify:

python -c "import serial; print(serial.__file__)"


It must point to:

...\Lib\site-packages\serial\


NOT vendored_libs.

✅ STEP 5 — Lock It in Your Build Process (VERY IMPORTANT)

If you are building ThonnySc for distribution:

Add pyserial to your build requirements.

Example:

If you use a requirements file:

pyserial
esptool


Then before packaging:

python -m pip install -r requirements.txt

🧹 STEP 6 — Clean Vendored Strategy (Professional Advice)

Keep vendored_libs ONLY for:

Small single-file libraries

Rare dependencies

Things that should NEVER conflict with pip

Avoid vendoring:

serial

requests

numpy

common library names

Because they WILL conflict.

🏗 STEP 7 — (Optional But Recommended)

Reorder sys.path so site-packages comes BEFORE vendored_libs.

Inside Thonny startup (if you want clean architecture), ensure:

site-packages


comes before:

vendored_libs


But removing serial is usually enough.