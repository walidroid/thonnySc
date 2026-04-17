import sys
import io

class FakeStream(io.StringIO):
    pass

sys.stderr = FakeStream()

try:
    raise TypeError("Test error")
except Exception as e:
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    try:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        print("Success!")
    except Exception as e2:
        print("Failed:", type(e2), e2)

sys.stderr.seek(0)
print("Buffer contents:", repr(sys.stderr.read()))
