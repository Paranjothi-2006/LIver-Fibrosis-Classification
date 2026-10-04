import torch
import torch.nn as nn
import torchvision.models as models

class MobileNetV3_ViT_Hybrid(nn.Module):
    def __init__(self, num_classes=5, embed_dim=256, num_heads=8, num_transformer_layers=2):
        super(MobileNetV3_ViT_Hybrid, self).__init__()
        
        # 1. Local Feature Extraction: MobileNetV3-Large Backbone
        mobilenet = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
        self.backbone = mobilenet.features  # Output: [B, 960, 7, 7]
        
        # 2. Token / Embedding Layer (Converts spatial feature map into patch tokens)
        self.conv_proj = nn.Conv2d(960, embed_dim, kernel_size=1)
        self.pos_embedding = nn.Parameter(torch.randn(1, 49, embed_dim))  # 7x7 = 49 tokens
        
        # 3. Vision Transformer Layer (Self-Attention)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, 
            nhead=num_heads, 
            dim_feedforward=512, 
            dropout=0.1, 
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_transformer_layers)
        
        # 4. Global Average Pooling for CNN Backbone
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # 5. Feature Fusion Layer (Combines CNN + ViT representations)
        self.fusion = nn.Sequential(
            nn.Linear(960 + embed_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        
        # 6. Final Softmax Classifier Head
        self.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        feat_map = self.backbone(x)  # [B, 960, 7, 7]
        
        # Global CNN features
        cnn_global = self.global_pool(feat_map).view(x.size(0), -1)  # [B, 960]
        
        # ViT Tokenization & Self-Attention
        tokens = self.conv_proj(feat_map)  # [B, embed_dim, 7, 7]
        tokens = tokens.flatten(2).permute(0, 2, 1)  # [B, 49, embed_dim]
        tokens = tokens + self.pos_embedding
        
        vit_out = self.transformer(tokens)  # [B, 49, embed_dim]
        vit_global = vit_out.mean(dim=1)  # [B, embed_dim]
        
        # Feature Fusion
        fused_features = torch.cat((cnn_global, vit_global), dim=1)
        fused = self.fusion(fused_features)
        
        # Final Output
        out = self.fc(fused)
        return out

if __name__ == "__main__":
    model = MobileNetV3_ViT_Hybrid(num_classes=5)
    dummy_input = torch.randn(2, 3, 224, 224)
    print("Model Output Shape:", model(dummy_input).shape)