# api.py
import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from graph.pipeline import build_pipeline
from state.agent_state import AgentState

app = FastAPI(title="MAS Code Review API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "model": "llama3:8b"}


@app.post("/analyze")
async def analyze_code(file: UploadFile = File(...)):
    """
    Accepts a .py file, runs it through the full
    MAS pipeline, and returns structured results.

    Args:
        file (UploadFile): The Python file to analyze.

    Returns:
        JSONResponse: Full pipeline results including
                      summary, bugs, fixes, and tests.
    """
    # Validate file type
    if not file.filename.endswith(".py"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .py files are accepted."}
        )

    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(
        suffix=".py",
        delete=False,
        mode="wb"
    ) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Initialize global state
        initial_state: AgentState = {
            "file_path": tmp_path,
            "raw_code": "",
            "code_summary": "",
            "functions": [],
            "imports": [],
            "complexity_score": 0,
            "bug_report": [],
            "lint_output": "",
            "security_issues": [],
            "fixed_code": "",
            "fix_summary": [],
            "test_code": "",
            "test_results": {},
            "final_report_path": "",
            "logs": [],
            "status": "running"
        }

        # Run full pipeline
        pipeline = build_pipeline()
        final_state = pipeline.invoke(initial_state)

        return JSONResponse({
            "status": final_state["status"],
            "code_summary": final_state["code_summary"],
            "functions": final_state["functions"],
            "imports": final_state["imports"],
            "complexity_score": final_state["complexity_score"],
            "bug_report": final_state["bug_report"],
            "lint_output": final_state["lint_output"],
            "security_issues": final_state["security_issues"],
            "fixed_code": final_state["fixed_code"],
            "fix_summary": final_state["fix_summary"],
            "test_code": final_state["test_code"],
            "test_results": final_state["test_results"],
            "final_report_path": final_state["final_report_path"],
            "logs": final_state["logs"]
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

    finally:
        # Always clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)