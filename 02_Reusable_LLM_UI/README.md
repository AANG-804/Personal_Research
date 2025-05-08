# 🚀 Reusable LLM UI

A modern, scalable, and reusable UI framework for Large Language Model (LLM) applications. This project provides a robust foundation for building AI-powered applications with a beautiful user interface and efficient backend architecture.

## 📋 Table of Contents
- [🚀 Reusable LLM UI](#-reusable-llm-ui)
  - [📋 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🛠️ Tech Stack](#️-tech-stack)
    - [Frontend](#frontend)
    - [Backend](#backend)
  - [📁 Project Structure](#-project-structure)
  - [🚀 Getting Started](#-getting-started)
    - [Prerequisites](#prerequisites)
    - [Frontend Setup](#frontend-setup)
    - [Backend Setup](#backend-setup)
  - [💻 Development](#-development)
    - [Frontend Development](#frontend-development)
    - [Backend Development](#backend-development)
  - [📚 API Documentation](#-api-documentation)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)

## ✨ Features

- 🎨 Modern and responsive UI design
- 🔄 Real-time chat interface
- 📱 Mobile-first approach
- 🔒 Secure API endpoints
- 🚀 Fast and efficient backend processing
- 📊 Easy integration with various LLM providers
- 🛠️ Customizable components
- 🌐 Scalable architecture

## 🛠️ Tech Stack

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Shadcn UI Components
- React Query
- Zustand (State Management)

### Backend
- FastAPI
- Python 3.11+
- SQLAlchemy
- Pydantic
- JWT Authentication
- Async Support

## 📁 Project Structure

```
Reusable_LLM_UI/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Next.js pages
│   │   ├── styles/         # Global styles
│   │   └── utils/          # Utility functions
│   └── public/             # Static assets
│
└── backend/                 # FastAPI backend application
    ├── config/             # Configuration files
    ├── models/             # Database models
    ├── routes/             # API endpoints
    ├── services/           # Business logic
    └── utils/              # Utility functions
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- Python 3.11+
- Git

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 💻 Development

### Frontend Development
- Run development server: `npm run dev`
- Build for production: `npm run build`
- Start production server: `npm start`
- Run tests: `npm test`

### Backend Development
- Start development server: `uvicorn main:app --reload`
- Run tests: `pytest`
- Generate API documentation: Visit `http://localhost:8000/docs`

## 📚 API Documentation

The API documentation is automatically generated using Swagger UI. Once the backend server is running, you can access it at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by [Your Name] 