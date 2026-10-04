# 🩺 HepatoVision AI: Clinical B-Mode Ultrasound Liver Fibrosis Staging System

HepatoVision AI is a full-stack clinical decision-support platform designed for automated B-mode ultrasound liver fibrosis staging using the METAVIR scale (F0–F4). The system features a **MobileNetV3-Large + Vision Transformer (ViT) Hybrid Model**, a high-performance **FastAPI** backend, and a medical-grade **React (Vite)** workstation interface.

---

## 📁 Project Structure

```text
Liver_Fibrosis_FullStack/
│
├── backend/                        # FastAPI Python Service
│   ├── main.py                     # API REST Endpoints & CORS Setup
│   ├── model.py                    # MobileNetV3 + ViT Hybrid Model Architecture
│   ├── report_gen.py               # ReportLab PDF Generation Module
│   ├── best_hybrid_model.pth       # Trained PyTorch Model Weights
│   └── requirements.txt            # Python Dependencies
│
├── frontend/                       # React (Vite) Workstation UI
│   ├── src/
│   │   ├── App.jsx                 # Main Clinical Dashboard Component
│   │   ├── App.css                 # Medical Workstation Stylesheet
│   │   └── main.jsx                # React App Entry Point
│   ├── index.html                  # HTML Shell
│   └── package.json                # Node Dependencies
│
└── README.md                       # System Setup & Deployment Guide



# Step 1: Open a terminal and navigate to the backend directory
cd backend

# Step 2: (Optional but Recommended) Create and activate a Python Virtual Environment
# On Windows:
python -m venv venv
venv\Scripts\activate
# On macOS/Linux:
# python3 -m venv venv
# source venv/bin/activate

# Step 3: Upgrade pip package manager
python -m pip install --upgrade pip

# Step 4: Install all required backend dependencies
python -m pip install -r requirements.txt

# Step 5: Start the FastAPI ASGI server on port 8000
# Note: Using 'python -m uvicorn' prevents Windows PATH command errors
python -m uvicorn main:app --reload --port 8000


# Step 1: Navigate to the frontend directory
cd frontend

# Note: If your setup created a nested subfolder (frontend/frontend), navigate into it:
# cd frontend

# Step 2: Install Node.js dependencies listed in package.json
npm install

# Step 3: Install Axios HTTP Client for API connectivity
npm install axios

# Step 4: Launch the React Vite development workstation
npm run dev