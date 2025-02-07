import asyncio
import uvicorn
import sys
from pathlib import Path
import subprocess

# Add project root to Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.api.main import app

async def run_fastapi():
    """Run FastAPI server."""
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

async def run_chainlit():
    """Run Chainlit server."""
    # Run Chainlit in a subprocess to avoid import conflicts
    process = subprocess.Popen(
        ["chainlit", "run", str(root_dir / "src" / "chat_interface.py"),  "-w","--port", "8501"],
        cwd=str(root_dir)
    )
    
    try:
        # Wait for the process
        await asyncio.get_event_loop().run_in_executor(None, process.wait)
    except Exception as e:
        process.kill()
        raise e

async def main():
    """Run both FastAPI and Chainlit servers."""
    try:
        print("Starting RoamMind servers...")
        print("FastAPI will be available at http://127.0.0.1:8000")
        print("Chainlit UI will be available at http://127.0.0.1:8501")
        
        # Run both servers concurrently
        await asyncio.gather(
            run_fastapi(),
            run_chainlit()
        )
    except KeyboardInterrupt:
        print("\nShutting down servers...")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServers stopped.")