# Zomathon: Two-Stage Hybrid Engine Stack

Welcome to the **Zomathon** project! This repository houses an advanced, cart-level intelligent cross-selling engine built with a powerful Two-Stage Hybrid Architecture. By combining deep learning with structural taxonomy, our system delivers highly accurate and context-aware food recommendations.

## 🌟 Architecture Overview

Our recommendation engine goes beyond basic string matching by utilizing a two-stage approach:
1. **Behavioral Recall (Stage 1):** A PyTorch Two-Tower neural network that learns implicit user interaction patterns to suggest items frequently bought together.
2. **Taxonomical Precision (Stage 2):** A Knowledge Graph powered by NetworkX that uses PageRank to enforce strict culinary laws. This ensures recommendations make logical sense (e.g., preventing cross-cuisine mixing or temperature clashes).

## 📂 Project Structure

- `/backend`: Contains the FastAPI server for the recommendation engine.
- `/backend/training_pipeline`: Contains the Machine Learning model training pipeline scripts.
- `/frontend`: Contains the user interface components (React/Vite).

## 🚀 Getting Started

There are two main ways to run this project: **Direct Execution** (running the pre-trained backend) and **Model Training** (retraining the neural network from scratch). Both have their own distinct setup requirements.

### Option 1: Direct Execution (FastAPI Backend + Frontend)

If you simply want to run the application using pre-trained data:

**1. Data Preparation**
You do not need to run the complex training pipeline. We provide the already compiled required files via a drive link:
- [🔗 Download items.csv and final_backend_embeddings.npy here (Placeholder Link)](https://drive.google.com/drive/folders/1rUQaQvkzjASKWW6h9melDxPy-5CfCgch?usp=sharing)

*Please download `items.csv` and `final_backend_embeddings.npy` from the drive link above and place them directly in the `backend/` directory.*

**2. Backend Setup**
Navigate to the backend directory, install the minimal API dependencies, and start the server.
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
*The API will be available at `http://localhost:8000`.*

**3. Frontend Setup**
Navigate to the frontend directory and start the web application.
```bash
cd frontend
npm install
npm run dev
```

### Option 2: Model Training Pipeline

If you want to edit the data, tweak the model, or retrain the Two-Tower neural network from scratch:

**1. Data Preparation**
You will need the raw restaurant data to feed into the catalog generator.
- [🔗 Download restaurants.csv here (Placeholder Link)](#)

*Please download `restaurants.csv` from the drive link above and place it inside the `backend/training_pipeline/` directory.*

**2. Training Setup & Execution**
The training pipeline requires heavy ML dependencies like PyTorch and Transformers. Navigate to the pipeline directory and install its specific requirements:

```bash
cd backend/training_pipeline
pip install -r requirements.txt
```

> **⚠️ Note for GPU Acceleration:** The `requirements.txt` installs the default PyTorch binaries. To train the Two-Tower model using CUDA (Nvidia GPU), please install the specific PyTorch wheel for your system from the official PyTorch website before running the training script.

Then, execute the pipeline scripts in order as detailed in the `/backend/README.md`.


