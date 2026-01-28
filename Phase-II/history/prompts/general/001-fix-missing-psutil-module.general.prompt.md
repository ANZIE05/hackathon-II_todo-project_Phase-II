---
id: "001"
title: "Fix Missing Psutil Module Error"
stage: "general"
date: "2026-01-24"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "001-backend-spec"
user: "user"
command: "Please carefully analyze my Todo project and identify, debug, and fix all these errors given below. Make sure the application works smoothly and correctly, without breaking any existing functionality."
labels:
  - "debugging"
  - "dependencies"
  - "module-error"
links:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
files:
  - "requirements.txt"
  - "src/api/monitoring.py"
  - "main.py"
tests: []
outcome: "Fixed ModuleNotFoundError by adding missing dependencies to requirements.txt"
evaluation: "Application now starts successfully without import errors"
---

## User Input

```
Please carefully analyze my Todo project and identify, debug, and fix all these errors given below.
Make sure the application works smoothly and correctly, without breaking any existing functionality.

"Process SpawnProcess-1:
Traceback (most recent call last):
  File "/usr/lib/python3.12/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/lib/python3.12/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/venv/lib/python3.12/site-packages/uvicorn/_subprocess.py", line 76, in subprocess_started
    target(sockets=sockets)
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
    config.load()
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 24, in import_from_string
    raise exc from None
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 24, in import_from_string
    raise exc from None
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/main.py", line 15, in <module>
    from src.api.monitoring import include_monitoring_routes
  File "/mnt/e/All Generative related items/Quarter-4/Hackathon-II-todo-project/Phase-II/src/api/monitoring.py", line 8,
in <module>
    import psutil
ModuleNotFoundError: No module named 'psutil'"
```

## Response

I have successfully analyzed and fixed the errors in your Todo project. Here's what was done:

### Issue Identified
The main error was a `ModuleNotFoundError: No module named 'psutil'` occurring when the application tried to start. This happened because:
- The `monitoring.py` file in `src/api/monitoring.py` was using `psutil` for system monitoring functions
- `psutil` was not included in the `requirements.txt` file
- The application failed to start because the required module was missing

### Fixes Applied

1. **Added missing `psutil` dependency**:
   - Added `psutil==5.9.7` to `requirements.txt`
   - Installed the package in the virtual environment

2. **Identified and added other missing dependencies**:
   - Added `bleach==6.1.0` (used for HTML sanitization in `src/utils/sanitize.py`)
   - Added `PyJWT==2.8.0` (used for JWT handling in `src/utils/jwt.py`)

3. **Verified all dependencies are now available**:
   - Tested that all required modules can be imported successfully
   - Verified the monitoring module works correctly
   - Confirmed the application can start without import errors

### Verification
- ✅ All required modules import successfully
- ✅ psutil functions work correctly (tested CPU and memory monitoring)
- ✅ Monitoring module loads without errors
- ✅ Main application imports without errors

The application should now start correctly without the ModuleNotFoundError. The system monitoring endpoints will also function properly with access to system metrics like CPU, memory, and disk usage.