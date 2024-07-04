import torch
import torch.nn as nn  # Import torch.nn and alias it as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np
import time

# Define the CustomModel class
class CustomModel(nn.Module):
    def __init__(self):
        super(CustomModel, self).__init__()
        self.resnet = models.resnet50(pretrained=True)
        num_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(num_features, 3)  # 3 classes: Caries, Gingivitis, Ulcers

    def forward(self, x):
        x = self.resnet(x)
        return x

def load_pytorch_model():
    model = CustomModel()
    state_dict = torch.load('C:\\Users\\shira\\Desktop\\FYP\\FinalizedModels\\resnet50.pth')

    # Print model keys and state_dict keys for debugging
    model_keys = set(model.state_dict().keys())
    state_dict_keys = set(state_dict.keys())
    print("Model keys:", model_keys)
    print("State_dict keys:", state_dict_keys)
    
    # Handle state dict key prefixing if necessary
    new_state_dict = {}
    for k, v in state_dict.items():
        if k.startswith('model.'):
            new_state_dict[k[6:]] = v  # Remove 'model.' prefix
        else:
            new_state_dict[k] = v

    missing_keys, unexpected_keys = model.load_state_dict(new_state_dict, strict=False)
    print("Missing keys:", missing_keys)
    print("Unexpected keys:", unexpected_keys)

    model.eval()  # Set the model to evaluation mode
    return model

model = load_pytorch_model()  # Load the model once when the app starts

def assess_image(image_path, model):
    # Simulate loading time
    time.sleep(3)

    # Load the image
    image = Image.open(image_path)
    
    # Preprocess the image as required by your model
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    image_tensor = preprocess(image).unsqueeze(0)  # Add batch dimension

    # Predict using the model
    with torch.no_grad():
        prediction = model(image_tensor)
    
    # Assuming the model returns probabilities, get the class with the highest probability
    predicted_class = np.argmax(prediction.numpy(), axis=1)[0]
    
    # Map the predicted class to a disease name
    class_names = ['Caries', 'Gingivitis', 'Mouth Ulcers']
    assessment = class_names[predicted_class]
    
    return assessment
