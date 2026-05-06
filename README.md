# INK IT Solutions - Inkie RAG Chatbot

Inkie is a sophisticated AI-powered virtual assistant designed for **INK IT Solutions**. Built using a Retrieval-Augmented Generation (RAG) architecture, Inkie provides accurate, context-aware information about INK IT's services, products, and technical solutions by retrieving data from a curated knowledge base.

##  Features

- **Multilingual Support**: Automatically detects and translates user queries into multiple languages (English, Arabic, French, Spanish, German).
- **RAG Architecture**: Combines real-time web scraping and vector search (Pinecone) to provide factual answers.
- **Intent-Based Interaction**: Differentiates between social talk and technical queries to maintain a professional persona.
- **LLM Agnostic**: Supports both cloud-based providers (OpenRouter) and local models (LM Studio).
- **Modern UI**: A sleek, responsive React-based chat interface.
- **Speech-to-Text**: Integrated voice recognition for a hands-free conversational experience.

---

##  Tech Stack

### Backend (Python)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework for building APIs.
- **LLM Integration**: [OpenAI SDK](https://github.com/openai/openai-python) (connected via **OpenRouter**) & **LM Studio** for local inference.
- **Vector Database**: [Pinecone](https://www.pinecone.io/) - Managed vector database for efficient similarity search.
- **Embeddings**: [Sentence-Transformers](https://www.sbert.net/) - For generating high-quality text embeddings.
- **Scraping & Processing**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) & [Requests](https://requests.readthedocs.io/).
- **Translation & Language**: `deep-translator` & `langdetect`.
- **Validation**: [Pydantic](https://docs.pydantic.dev/) - Data validation and settings management.

### Frontend (React)
- **Bundler**: [Vite](https://vitejs.dev/) - Fast next-generation frontend tooling.
- **UI Library**: [React 19](https://react.dev/).
- **Styling**: [Tailwind CSS 4](https://tailwindcss.com/) - Utility-first CSS framework.
- **Animations**: [Framer Motion](https://www.framer.com/motion/) - For smooth interactive elements.
- **Icons**: [Lucide React](https://lucide.dev/).
- **Speech**: `react-speech-recognition` - For voice-to-text capabilities.
- **State/API**: [Axios](https://axios-http.com/) for backend communication.

---


##  Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENV=your_pinecone_environment (e.g., us-east-1)
PINECONE_INDEX=your_pinecone_index_name
PINECONE_HOST=your_pinecone_host_url
LLM_PROVIDER=openrouter # or lm_studio

```

---

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd bot-inkIT-RAG
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/Scripts/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

---

##  How to Run

### Run the Backend
From the `backend/` directory:
```bash
python main.py
```
Alternatively, using uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```
The backend will be available at `http://127.0.0.1:8000`.

### Run the Frontend
From the `frontend/` directory:
```bash
npm run dev
```
The frontend will be available at the URL provided by Vite (usually `http://localhost:1234`).

---

## 📂 Project Structure

- `backend/`: FastAPI application, RAG logic, and scrapers.
- `frontend/`: React application with chat components and styling.
- `data/`: Local storage for scraped data and knowledge base.

---

## 👤 Author
Developed for **INK IT Solutions**.
