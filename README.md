# Smart-support-copilot
An intelligent **AI Copilot** powered by **Retrieval-Augmented Generation (RAG)** and a **custom-trained Machine Learning model**, built to assist customer support teams with real-time, context-aware answers.
Built using **React.js**, **Flask**, and **Scikit-learn**, featuring live analytics, document chat, dark mode, and production-ready deployment.

---
 <img width="1897" height="872" alt="image" src="https://github.com/user-attachments/assets/05b0ef2e-279e-42a2-87fc-220634db4462" />

## 🤖 Machine Learning & AI Intelligence

### 🔹 Custom Classification Model
- Trained using **Scikit-learn (Logistic Regression)**  
- Predicts **Query Category**, **Priority**, and **Sentiment**
- Serialized with `joblib` for fast, production-ready inference  

### 🔹 RAG (Retrieval-Augmented Generation)
- Uses **Sentence-Transformers (MiniLM-L6-v2)** for embeddings  
- Retrieves relevant chunks from uploaded **PDF/DOCX** files  
- Combines retrieved text + model prediction for accurate answers  

### 🔹 Sentiment Analysis
- Integrated **VADER Sentiment Analyzer** for emotional tone detection  
- Enhances AI responses with empathy and tone consistency  

💡 *Together, these enable document-aware, emotionally intelligent AI support.*

---

## Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Frontend** | React.js, Tailwind CSS, Recharts, html2canvas, jsPDF |
| **Backend** | Python, Flask, Flask-CORS, SQLite |
| **AI / ML** | Scikit-learn, Sentence-Transformers, VADER, NumPy |
| **APIs** | RESTful (POST `/ask`, GET `/history`, POST `/feedback`, DELETE `/delete`) |
| **DevOps / Tools** | Git, VS Code, PowerShell, Local Flask-React deployment |

---
##  Features

-  **RAG-powered AI Chat** (contextual document understanding)  
-  **Dark Mode** with modern UI  
-  **AI Typing Animation** for real chat feel  
-  **Live Dashboard** (usage metrics, charts)  
-  **PDF Export** of chat sessions  
-  **Delete Messages** + feedback history  
-  **Feedback System** (user sentiment & accuracy tracking)  
-  **Single-command Deploy** (build & serve from Flask)

---

## 🧪 Run Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend
cd frontend
npm install
npm run build
