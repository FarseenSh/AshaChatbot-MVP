# AshaChatbot 🤖

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/React-18.2.0-61DAFB.svg" alt="React Version">
  <img src="https://img.shields.io/badge/Next.js-14.1.0-000000.svg" alt="Next.js Version">
  <img src="https://img.shields.io/badge/FastAPI-0.113.0-009688.svg" alt="FastAPI Version">
  <img src="https://img.shields.io/badge/LangChain-0.1.8-purple.svg" alt="LangChain Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</div>

---

## 🌟 About

**AshaChatbot** is an AI-powered assistant designed to enhance user engagement on the JobsForHer Foundation platform by offering relevant insights and seamless interactions for women's career advancement. It leverages a Retrieval-Augmented Generation (RAG) system built with LangChain and Gemini 2.5 Pro to provide personalized job recommendations, event information, and career guidance.

## 🔑 Key Features

- **📊 Job Recommendations**: Provides personalized job suggestions based on user queries from structured datasets
- **📅 Event Information**: Shares details about upcoming community events and sessions
- **💡 Career Insights**: Delivers guidance on women's career advancement and empowerment
- **🛡️ Ethical AI**: Detects and reframes gender-biased questions to provide factual, empowering responses
- **💬 Conversational Interface**: Maintains context for natural, flowing conversations

## 🏗️ Architecture

AshaChatbot employs a modern architecture using:

- **Backend**: Python FastAPI with LangChain RAG pipeline
- **LLM**: Gemini 2.5 Pro (via OpenRouter)
- **Vector Database**: ChromaDB for efficient semantic search
- **Frontend**: Next.js with React 18 and Tailwind CSS
- **UI Components**: shadcn/ui for a clean, responsive interface

## 📦 Dependency Versions

### Backend
| Package | Version |
|---------|---------|
| Python | 3.10+ |
| LangChain | 0.1.8 |
| FastAPI | 0.113.0 |
| ChromaDB | 0.5.3 |
| OpenRouter | 1.0 |
| Pandas | 2.2.0 |
| Gradio | 4.13.0 |

### Frontend
| Package | Version |
|---------|---------|
| Next.js | 14.1.0 |
| React | 18.2.0 |
| Tailwind CSS | 3.4.1 |
| react-icons | 4.12.0 |
| framer-motion | 10.16.4 |

## 🚀 Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/FarseenSh/AshaChatbot-MVP.git
cd AshaChatbot-MVP
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run the setup script**

```bash
chmod +x setup.sh
./setup.sh
```

4. **Start the backend server**

```bash
cd backend
source ../venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

5. **Start the frontend development server**

```bash
cd frontend
npm run dev
```

## 🐳 Docker Deployment

For containerized deployment:

```bash
docker-compose up -d
```

## 📱 API Endpoints

- **POST /api/query**: Process a user query and get a response
- **GET /api/jobs**: Search for job listings based on a query
- **GET /api/sessions**: Get upcoming events and sessions
- **POST /api/detect-bias**: Detect potential gender bias in a query
- **GET /api/healthcheck**: Check if the API is running

## 🛠️ Project Structure

```
AshaChatbot-MVP/
├── backend/
│   ├── data/
│   │   ├── job_listing_data.csv     # Job listings
│   │   └── Session Details.json     # Event information
│   ├── api.py                       # FastAPI server
│   ├── main.py                      # Core RAG system
│   ├── job_listing_parser.py        # Job data processor
│   ├── bias_detection.py            # Gender bias handling
│   ├── session_processor.py         # Event data processor
│   └── system_prompt.md             # System prompt for the LLM
├── frontend/                        # Next.js frontend application
├── .env.example                     # Example environment variables
├── requirements.txt                 # Backend dependencies
├── docker-compose.yml               # Docker configuration
└── README.md                        # This file
```

## 📝 Development Notes

### Frontend Compatibility

The frontend uses React 18.2.0 instead of React 19 due to compatibility issues with various UI libraries including shadcn/ui and framer-motion. The codebase uses react-icons instead of lucide-react for better compatibility.

### OpenRouter Integration

The application uses OpenRouter to access Gemini 2.5 Pro. If you encounter API errors, verify that you have the correct version of the openrouter package (1.0).

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- JobsForHer Foundation for the problem statement
- OpenRouter for providing access to Gemini 2.5 Pro
- LangChain for the excellent RAG framework
- shadcn/ui for the beautiful UI components