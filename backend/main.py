import os
import io
import base64
import torch
import torch.nn.functional as F
import numpy as np
import cv2
import datetime
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from torchvision import transforms

from model import MobileNetV3_ViT_Hybrid
from report_gen import generate_pdf_report

app = FastAPI(title="Liver Fibrosis Diagnostic API")

# Enable CORS for React Frontend (running on localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load Model
model = MobileNetV3_ViT_Hybrid(num_classes=5)
MODEL_PATH = "best_hybrid_model.pth"

if os.path.exists(MODEL_PATH):
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.to(device)
    model.eval()
    print("✅ Model loaded successfully!")
else:
    print("⚠️ Warning: 'best_hybrid_model.pth' not found.")

class_names = ['F0', 'F1', 'F2', 'F3', 'F4']

# Grad-CAM Class
class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)
        
    def save_activation(self, module, input, output):
        self.activations = output
        
    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]
        
    def generate(self, input_tensor, target_class=None):
        self.model.eval()
        output = self.model(input_tensor)
        if target_class is None:
            target_class = torch.argmax(output, dim=1).item()
            
        self.model.zero_grad()
        loss = output[0, target_class]
        loss.backward()
        
        gradients = self.gradients.data.cpu().numpy()[0]
        activations = self.activations.data.cpu().numpy()[0]
        weights = np.mean(gradients, axis=(1, 2))
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        
        for i, w in enumerate(weights):
            cam += w * activations[i]
            
        cam = np.maximum(cam, 0)
        cam = cv2.resize(cam, (224, 224))
        cam = cam - np.min(cam)
        cam = cam / (np.max(cam) + 1e-8)
        return cam, target_class

@app.post("/api/predict")
async def predict_fibrosis(
    file: UploadFile = File(...),
    name: str = Form("John Doe"),
    patient_id: str = Form("P10023"),
    age: int = Form(30),
    gender: str = Form("Male")
):
    try:
        # Read uploaded image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        val_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = val_transforms(image).unsqueeze(0).to(device)
        
        # Inference
        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.softmax(outputs, dim=1)[0]
            pred_idx = torch.argmax(probs).item()
            pred_class = class_names[pred_idx]
            confidence = float(probs[pred_idx].item() * 100)

        # Grad-CAM Heatmap Overlay
        grad_cam = GradCAM(model, model.backbone[-1])
        heatmap, _ = grad_cam.generate(input_tensor, target_class=pred_idx)
        
        img_np = np.array(image.resize((224, 224))) / 255.0
        heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB) / 255.0
        overlay = np.clip(0.6 * img_np + 0.4 * heatmap_colored, 0, 1)

        # Convert overlay image to Base64 String for React rendering
        overlay_bgr = cv2.cvtColor((overlay * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.png', overlay_bgr)
        overlay_base64 = base64.b64encode(buffer).decode('utf-8')

        # Side-by-Side Image for PDF Embed
        fig_side = np.hstack(((img_np * 255).astype(np.uint8), (overlay * 255).astype(np.uint8)))
        temp_cam_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        cv2.imwrite(temp_cam_file.name, cv2.cvtColor(fig_side, cv2.COLOR_RGB2BGR))

        # Generate Clinical PDF Report
        patient_dict = {
            'name': name,
            'id': patient_id,
            'age': age,
            'gender': gender,
            'date': str(datetime.date.today())
        }
        
        pdf_filename = f"Report_{patient_id}.pdf"
        generate_pdf_report(patient_dict, pred_class, confidence, temp_cam_file.name, output_pdf_path=pdf_filename)

        # Probabilities Dict
        prob_distribution = {class_names[i]: float(probs[i].item() * 100) for i in range(5)}

        return {
            "predicted_stage": pred_class,
            "confidence": round(confidence, 2),
            "probabilities": prob_distribution,
            "overlay_image": f"data:image/png;base64,{overlay_base64}",
            "report_filename": pdf_filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-report/{filename}")
async def download_report(filename: str):
    if os.path.exists(filename):
        return FileResponse(path=filename, filename=filename, media_type='application/pdf')
    raise HTTPException(status_code=404, detail="PDF report not found.")