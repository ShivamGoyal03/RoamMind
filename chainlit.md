## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/ShivamGoyal03/RoamMind.git
   cd RoamMind/src
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the API
Start the FastAPI application using:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```
You can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`