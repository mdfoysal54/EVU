import sys
import io
import traceback
from app.agent.tools.base import ToolExecution


class PythonExecTool:
    name = "python_exec"
    timeout_seconds: int = 10

    def run(self, code: str) -> ToolExecution:
        cleaned_code = code.strip()
        if cleaned_code.startswith("```python"):
            cleaned_code = cleaned_code[9:]
        elif cleaned_code.startswith("```"):
            cleaned_code = cleaned_code[3:]
        if cleaned_code.endswith("```"):
            cleaned_code = cleaned_code[:-3]
        cleaned_code = cleaned_code.strip()

        if not cleaned_code:
            return ToolExecution(
                name=self.name,
                input=code,
                output="No executable Python code provided.",
                success=False,
            )

        # Restricted execution globals
        safe_globals = {
            "__builtins__": {
                "abs": abs,
                "all": all,
                "any": any,
                "bin": bin,
                "bool": bool,
                "dict": dict,
                "enumerate": enumerate,
                "filter": filter,
                "float": float,
                "format": format,
                "hex": hex,
                "int": int,
                "isinstance": isinstance,
                "len": len,
                "list": list,
                "map": map,
                "max": max,
                "min": min,
                "oct": oct,
                "ord": ord,
                "pow": pow,
                "print": print,
                "range": range,
                "round": round,
                "set": set,
                "sorted": sorted,
                "str": str,
                "sum": sum,
                "tuple": tuple,
                "zip": zip,
            }
        }
        safe_locals = {}

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_stdout = io.StringIO()
        redirected_stderr = io.StringIO()

        try:
            sys.stdout = redirected_stdout
            sys.stderr = redirected_stderr
            exec(cleaned_code, safe_globals, safe_locals)
            stdout_str = redirected_stdout.getvalue()
            stderr_str = redirected_stderr.getvalue()

            output = stdout_str
            if stderr_str:
                output += f"\n[stderr]:\n{stderr_str}"
            if not output.strip():
                output = "Code executed successfully with no console output."

            return ToolExecution(
                name=self.name,
                input=cleaned_code,
                output=output.strip(),
                success=True,
            )
        except Exception:
            err = traceback.format_exc()
            return ToolExecution(
                name=self.name,
                input=cleaned_code,
                output=f"Execution error:\n{err}",
                success=False,
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


python_exec_tool = PythonExecTool()