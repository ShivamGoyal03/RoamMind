# Travel AI Assistant

## Key Features
- **Conversational Interface:** Engage in natural language conversations for travel planning.
- **Multi-Domain Support:** Supports flight, hotel, restaurant, and excursion recommendations.
- **Semantic Kernel Integration:** Leverages advanced AI to process user input and generate precise responses.
- **Scalable Architecture:** Modular design with clearly separated layers for API, business logic, and infrastructure.
- **Custom Exception Handling:** Robust error handling for seamless user experience.

## Core Capabilities
- **User Input Processing:** Processes travel-related queries and extracts parameters.
- **Conversation Management:** Maintains conversation state through an orchestrator.
- **Information Extraction:** Uses dedicated skills for extracting flight, hotel, restaurant, and excursion details.
- **Data Enhancement:** Enhances search results and detailed information with LLM responses powered by Azure OpenAI.
- **Dependency Injection:** Utilizes dependency modules for orchestrator and infrastructure components ensuring loose coupling.

## Technical Features
- **FastAPI:** Provides a high-performance API for handling requests.
- **Azure OpenAI:** Integrates with Azure OpenAI for advanced language processing.
- **Cosmos DB Integration:** Uses Cosmos DB for repository and data storage purposes.
- **Modular Codebase:** Structured into multiple directories including `api`, `core`, `infrastructure`, `models`, `skills`, and `utils`.
- **Logging & Validation:** Built-in logging and validation utilities for efficient debugging and error handling.

## Project Structure
```
src
├── exceptions.py
├── run.py
├── chat_interface.py
├── __init__.py
├── api
│   ├── dependencies.py
│   ├── main.py
│   └── __init__.py
├── core
│   ├── config.py
│   ├── models.py
│   ├── orchestrator.py
│   └── __init__.py
├── infrastructure
│   ├── azure_openai.py
│   ├── cosmos_repository.py
│   └── __init__.py
├── models
│   ├── excursion.py
│   ├── flight.py
│   ├── hotel.py
│   ├── restaurant.py
│   ├── user.py
│   └── __init__.py
├── skills
│   ├── excursion_skill.py
│   ├── flight_skill.py
│   ├── hotel_skill.py
│   ├── restaurant_skill.py
│   └── __init__.py
├── utils
│   ├── currency.py
│   ├── date_helper.py
|   ├── location_mapper.py
│   ├── logger.py
│   ├── validation.py
│   └── __init__.py
```

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

## Content Owners

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->

<table>
<tr>
    <td align="center"><a href="https://github.com/ShivamGoyal03">
        <img src="https://github.com/ShivamGoyal03.png" width="100px;" alt="Shivam Goyal"/><br />
        <sub><b>Shivam Goyal</b></sub>
    </a><br />
    </td>
</tr></table>

## Usage

### Running the Application

Start both FastAPI and Chainlit servers with a single command:
```bash
python src/run.py
```

This will start:
- FastAPI backend at `http://127.0.0.1:8000`
- Chainlit UI at `http://127.0.0.1:8501`
- API docs at `http://127.0.0.1:8000/api/docs`

## Configuration
RoamMind is configured via environment variables and the `src/core/config.py` file. Key configuration parameters include:
- `AZURE_OPENAI_ENDPOINT`: The endpoint URL for Azure OpenAI.
- `AZURE_OPENAI_API_VERSION`: The API version for Azure OpenAI.
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
- Cosmos DB connection details (if applicable).



## Additional Information
- **Logging:** A custom logger is implemented in `src/utils/logger.py` to track application activity.
- **Error Handling:** Custom exceptions are defined in `src/exceptions.py` for precise error management.
- **Skills Integration:** The `src/skills` directory contains skills for handling domain-specific tasks like flight search, hotel booking, restaurant recommendations, and excursion planning.

## Development

### Running Servers Separately
For development, you can run the servers separately:

1. **FastAPI:**
   ```bash
   uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Chainlit:**
   ```bash
   chainlit run src/chat_interface.py --port 8501
   ```

>  [!NOTE]
> RoamMind is a fictional project created solely as a template and does not represent a real product.
> It serves as the core logic for building AI agent instructions and is not fully production-ready. Contributions are welcome if you want to enhance it. 
> This template provides a foundational framework for a Travel AI Assistant, which you can customize to suit your requirements.

---
For more information, check out the resources:
- [AI Agents For Beginner Course](https://github.com/microsoft/ai-agents-for-beginners/)
- [Getting Started with Azure AI Studio](https://techcommunity.microsoft.com/blog/educatordeveloperblog/getting-started-with-azure-ai-studio/4095602?wt.mc_id=studentamb_258691)
- [Fundamentals of AI agents on Azure](https://learn.microsoft.com/en-us/training/modules/ai-agent-fundamentals/?wt.mc_id=studentamb_258691)
- [Azure AI Discord](https://aka.ms/AzureAI/Discord)