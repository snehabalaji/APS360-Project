# -*- coding: utf-8 -*-
"""
Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KrOi_9sE8de2kcxBErPpi4Nl0kOsN_2f

"""

###Imports
import numpy as np
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torch.utils.data import SubsetRandomSampler, DataLoader, Subset, Dataset
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import torchvision.datasets as datasets
import matplotlib.pyplot as plt
import cv2
from collections import Counter
import os
from PIL import Image
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report, accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split, GridSearchCV
import random
from skimage.feature import hog
from sklearn.preprocessing import StandardScaler
from sklearn import svm
import seaborn as sns

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

from google.colab import drive
drive.mount('/content/drive')

"""#1. Data Processing

##Testing Processing Techniques
"""

root_dir = "/content/drive/MyDrive/Fourth Year/APS360/APS360 Project/Data/Raw Images/"
transform = transforms.Compose([
    transforms.Resize((128, 128)),  # Resize all images to 128x128, this is uniform resolution
    transforms.ToTensor()           # Converting images to tensors
])

dataset = datasets.ImageFolder(root=root_dir, transform=transform)
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

# Show the number of images in each class
class_names = dataset.classes
class_counts = Counter(dataset.targets)
print("Number of images per class:")
for class_name, count in zip(class_names, [class_counts[i] for i in range(len(class_names))]):
    print(f"{class_name}: {count}")

# Function to visualize images
def imshow(imgs, labels, class_names):
    imgs = imgs.numpy().transpose((0, 2, 3, 1))  # Convert to (H, W, C)
    fig, axes = plt.subplots(1, len(imgs), figsize=(12, 4))
    for i, (img, label) in enumerate(zip(imgs, labels)):
        axes[i].imshow(np.clip(img, 0, 1))  # Clip to valid range
        axes[i].set_title(class_names[label])
        axes[i].axis("off")
    plt.show()

# Get a batch of images
data_iter = iter(dataloader)
images, labels = next(data_iter)

# Get class names
class_names = dataset.classes

# Show images before processing
imshow(images, labels, class_names)

#NOISE REDUCTION
def denoise_image(img):
    img = (img * 255).astype(np.uint8)  # Convert to uint8 format
    img_denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)  # Apply Non-Local Means Denoising for color images
    return img_denoised.astype(np.float32) / 255.0  # Normalize back to [0, 1] range

# Function to show images
def imshow(imgs, labels, class_names, denoise=False):
    imgs = imgs.numpy().transpose((0, 2, 3, 1))  # Convert to (H, W, C)
    if denoise:
        imgs = np.array([denoise_image(img) for img in imgs])
    fig, axes = plt.subplots(1, len(imgs), figsize=(12, 4))
    for i, (img, label) in enumerate(zip(imgs, labels)):
        axes[i].imshow(np.clip(img, 0, 1))  # Clip to valid range
        axes[i].set_title(class_names[label])
        axes[i].axis("off")
    plt.show()

# Get a batch of images
data_iter = iter(dataloader)
images, labels = next(data_iter)

# Get class names
class_names = dataset.classes

# Show original images
imshow(images, labels, class_names)

# Show denoised images
imshow(images, labels, class_names, denoise=True)

# CONTRAST MAPPING
def contrast_map(img):
    img = (img * 255).astype(np.uint8)  # Convert to uint8 format
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)  # Convert to LAB color space
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))  # Apply CLAHE to L channel
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    img_contrast = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)  # Convert back to RGB
    return img_contrast.astype(np.float32) / 255.0  # Normalize back to [0, 1] range

# Function to show images
def imshow(imgs, labels, class_names, contrast=False):
    imgs = imgs.numpy().transpose((0, 2, 3, 1))  # Convert to (H, W, C)
    if contrast:
        imgs = np.array([contrast_map(img) for img in imgs])
    fig, axes = plt.subplots(1, len(imgs), figsize=(12, 4))
    for i, (img, label) in enumerate(zip(imgs, labels)):
        axes[i].imshow(np.clip(img, 0, 1))  # Clip to valid range
        axes[i].set_title(class_names[label])
        axes[i].axis("off")
    plt.show()

# Get a batch of images
data_iter = iter(dataloader)
images, labels = next(data_iter)

# Get class names
class_names = dataset.classes

# Show original images
imshow(images, labels, class_names)

# Show contrast-enhanced images
imshow(images, labels, class_names, contrast=True)

#STANDARDIZATION
def standardize_image(img):
    mean = np.mean(img, axis=(0, 1), keepdims=True)  # Compute mean per channel
    std = np.std(img, axis=(0, 1), keepdims=True)  # Compute std per channel
    standardized_img = (img - mean) / (std + 1e-8)  # Standardize with small epsilon to avoid division by zero
    standardized_img = standardized_img * 0.2 + 0.5  # Scale to reduce contrast
    return np.clip(standardized_img, 0, 1)  # Clip values to valid range

# Function to show images
def imshow(imgs, labels, class_names, standardize=False):
    imgs = imgs.numpy().transpose((0, 2, 3, 1))  # Convert to (H, W, C)
    if standardize:
        imgs = np.array([standardize_image(img) for img in imgs])
    fig, axes = plt.subplots(1, len(imgs), figsize=(12, 4))
    for i, (img, label) in enumerate(zip(imgs, labels)):
        axes[i].imshow(np.clip(img, 0, 1))  # Clip to valid range
        axes[i].set_title(class_names[label])
        axes[i].axis("off")
    plt.show()

# Get a batch of images
data_iter = iter(dataloader)
images, labels = next(data_iter)

# Get class names
class_names = dataset.classes

# Show original images
imshow(images, labels, class_names)

# Show standardized images
imshow(images, labels, class_names, standardize=True)

"""##Applying Processing Techniques"""

root_dir = "/content/drive/MyDrive/Fourth Year/APS360/APS360 Project/Data/Raw Images/"

# Define transform pipeline
transform = transforms.Compose([
    transforms.Resize((128, 128)),  # Resize all images to 128x128
    transforms.ToTensor(),  # Convert to tensor
    transforms.Lambda(lambda img: img.permute(1, 2, 0).numpy()),  # Convert (C, H, W) to (H, W, C)
    transforms.Lambda(lambda img: standardize_image(img)),  # Apply standardization
    transforms.Lambda(lambda img: contrast_map(img)),  # Apply contrast mapping
    transforms.Lambda(lambda img: denoise_image(img)),  # Apply denoising
    transforms.Lambda(lambda img: torch.tensor(img).permute(2, 0, 1))  # Convert back to (C, H, W) tensor
])

# Load dataset with preprocessing
dataset = datasets.ImageFolder(root=root_dir, transform=transform)

"""##Proportional Stratified Sampling Without Replacement"""

# Extract labels for stratified splitting
labels = np.array(dataset.targets)

# Stratified split
train_idx, temp_idx, train_labels, temp_labels = train_test_split(
    np.arange(len(dataset)), labels, stratify=labels, test_size=0.30, random_state=42
)
val_idx, test_idx = train_test_split(
    temp_idx, stratify=temp_labels, test_size=0.50, random_state=42
)

# Create dataset subsets
train_dataset = Subset(dataset, train_idx)
val_dataset = Subset(dataset, val_idx)
test_dataset = Subset(dataset, test_idx)

"""##Data Augmentation (Training Dataset)"""

# Define Augmentations
augmentation_transforms = transforms.Compose([
    transforms.RandomRotation(30),  # Rotate image randomly up to 30 degrees
    transforms.RandomHorizontalFlip(p=0.5),  # Flip image horizontally
    transforms.RandomResizedCrop(128, scale=(0.8, 1.0)),  # Random crop
    transforms.RandomApply([transforms.GaussianBlur(kernel_size=(5, 5))], p=0.3),  # Blur with 30% probability
    transforms.RandomApply([transforms.Lambda(lambda x: x + 0.05 * torch.randn_like(x))], p=0.3)  # Add noise with 30% probability
])

class BalancedDataset(Dataset):
    def __init__(self, dataset, full_dataset, augmentation_transforms):
        self.dataset = dataset
        self.full_dataset = full_dataset
        self.augmentation_transforms = augmentation_transforms
        # Extract labels from the subset dataset
        self.targets = np.array([full_dataset.targets[i] for i in dataset.indices])
        # Compute class distribution in the training subset
        self.class_counts = Counter(self.targets)
        # Find the largest class count to balance all classes
        self.max_samples = max(self.class_counts.values())
        # Get indices of images for each class
        self.indices_per_class = self.get_class_indices()
        # Generate a list of indices that creates a balanced dataset
        self.balanced_indices = self.generate_balanced_indices()

    def get_class_indices(self):
        class_indices = {}
        for cls in self.class_counts.keys():
            class_indices[cls] = []
        for idx, label in zip(self.dataset.indices, self.targets):
            class_indices[label].append(idx)
        return class_indices

    def generate_balanced_indices(self):
        balanced_indices = []
        for cls, indices in self.indices_per_class.items():
            num_samples = len(indices)
            num_to_add = self.max_samples - num_samples
            # Keep original indices
            new_class_indices = indices.copy()
            # Add extra augmented samples if necessary
            if num_to_add > 0:
                extra_indices = random.choices(indices, k=num_to_add)
                new_class_indices.extend(extra_indices)
            # Add to final dataset
            balanced_indices.extend(new_class_indices)
        return balanced_indices

    def __len__(self):
        return len(self.balanced_indices)

    def __getitem__(self, idx):
        original_idx = self.balanced_indices[idx]
        img, label = self.full_dataset[original_idx]
        # Apply augmentation only to oversampled images
        if self.balanced_indices.count(original_idx) > 1:
            img = self.augmentation_transforms(img)
        return img, label

balanced_train_dataset = BalancedDataset(train_dataset, dataset, augmentation_transforms)

"""##Check Class Distribution"""

def dataset_class_distribution(subset, name):
    # Get the mapping from index to class
    idx_to_class = {v: k for k, v in subset.dataset.class_to_idx.items()}

    # Access the labels using subset.indices
    subset_labels = [subset.dataset.targets[i] for i in subset.indices]

    # Count the occurrences of each label
    label_counts = Counter(subset_labels)

    # Print label distribution
    print(f"\n{name} label distribution:")
    for label, count in sorted(label_counts.items()):
        class_name = idx_to_class[label]
        print(f"{class_name}: {count}")

    print(f"Total samples: {sum(label_counts.values())}")

dataset_class_distribution(train_dataset, "Train Dataset")
dataset_class_distribution(val_dataset, "Validation Dataset")
dataset_class_distribution(test_dataset, "Test Dataset")

print(f"\nLength of balanced_train_dataset: {len(balanced_train_dataset)}")

"""##Create Data Loaders"""

batch_size = 64

train_loader = DataLoader(balanced_train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

"""#2. Baseline Model"""

# Function to extract HOG features from a dataset
def extract_hog_features(data_loader):
    hog_features = []
    labels = []

    for images, targets in data_loader:
        for i in range(images.size(0)):
            # Convert tensor to numpy array and to grayscale
            image = images[i].numpy().transpose(1, 2, 0)
            gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Extract HOG features
            features, _ = hog(gray_image, orientations=9, pixels_per_cell=(8, 8),
                              cells_per_block=(2, 2), block_norm='L2-Hys', visualize=True)
            hog_features.append(features)
            labels.append(targets[i].item())

    return np.array(hog_features), np.array(labels)

# Extract features from each dataset
X_train, y_train = extract_hog_features(train_loader)
X_test, y_test = extract_hog_features(test_loader)

# Feature scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Hyperparameter tuning with GridSearchCV
param_grid = {'C': [1, 10], 'kernel': ['rbf', 'poly'], 'gamma': ['scale', 'auto']}
model = GridSearchCV(svm.SVC(), param_grid, cv=3)
model.fit(X_train, y_train)

print(f"Best parameters: {model.best_params_}")


# Evaluate model on test set
test_predictions = model.predict(X_test)
print("Test Accuracy:", accuracy_score(y_test, test_predictions))
print("Test Classification Report:\n", classification_report(y_test, test_predictions))

# Confusion matrix for test set
cm = confusion_matrix(y_test, test_predictions)
ConfusionMatrixDisplay(cm).plot()
plt.show()

"""#3. Primary Model"""

class DentalDiagnosisCNN(nn.Module):
    def __init__(self, num_classes=6):
        super(DentalDiagnosisCNN, self).__init__()

        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(32)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(64)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        self.conv4 = nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1)
        self.bn4 = nn.BatchNorm2d(128)

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x1 = F.relu(self.bn1(self.conv1(x)))
        x1 = self.pool(x1)

        x2 = F.relu(self.bn2(self.conv2(x1)))
        x2 = self.pool(x2)

        x3 = F.relu(self.bn3(self.conv3(x2)))
        x3 = self.pool(x3)

        x4 = F.relu(self.bn4(self.conv4(x3)))
        x4 = self.pool(x4)

        x = torch.flatten(x4, start_dim=1)
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

model = DentalDiagnosisCNN(num_classes=9)
criterion = nn.CrossEntropyLoss()

def train_net(model, model_name, learning_rate=0.001, num_epochs=10, train_loader=train_loader, val_loader=val_loader, criterion=criterion):
    # Fixed PyTorch random seed for reproducible result
    torch.manual_seed(1000)
    model.to(device)

    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Set up numpy arrays to store the training/test loss/err
    train_err = np.zeros(num_epochs)
    train_loss = np.zeros(num_epochs)
    val_err = np.zeros(num_epochs)
    val_loss = np.zeros(num_epochs)

    # Train the network
    start_time = time.time()
    for epoch in range(num_epochs):
        model.train()
        total_train_loss = 0.0
        total_train_err = 0.0
        total_epoch = 0
        for i, (inputs, labels) in enumerate(train_loader, 0):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            preds = outputs.argmax(dim=1)
            corr = preds != labels
            total_train_err += corr.sum().item()
            total_train_loss += loss.item()
            total_epoch += len(labels)

        train_err[epoch] = float(total_train_err) / total_epoch
        train_loss[epoch] = float(total_train_loss) / (i+1)

        model.eval()
        total_val_loss = 0.0
        total_val_err = 0.0
        total_epoch = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)

                preds = outputs.argmax(dim=1)
                corr = preds != labels
                total_val_err += corr.sum().item()
                total_val_loss += loss.item()
                total_epoch += len(labels)

        val_err[epoch] = float(total_val_err) / total_epoch
        val_loss[epoch] = float(total_val_loss) / len(val_loader)

        print(("Epoch {}: Train err: {}, Train loss: {} |"+
               "Validation err: {}, Validation loss: {}").format(
                   epoch + 1,
                   train_err[epoch],
                   train_loss[epoch],
                   val_err[epoch],
                   val_loss[epoch]))
    print('Finished Training')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Total time elapsed: {:.2f} seconds".format(elapsed_time))

    # Write the train/test loss/err into CSV file for plotting
    np.savetxt("{}_train_err.csv".format(model_name), train_err)
    np.savetxt("{}_train_loss.csv".format(model_name), train_loss)
    np.savetxt("{}_val_err.csv".format(model_name), val_err)
    np.savetxt("{}_val_loss.csv".format(model_name), val_loss)

train_net(model, 'DentalDiagnosisCNN', learning_rate=0.001, num_epochs=10, train_loader=train_loader, val_loader=val_loader)

train_err = np.loadtxt("DentalDiagnosisCNN_train_err.csv")
val_err = np.loadtxt("DentalDiagnosisCNN_val_err.csv")
train_loss = np.loadtxt("DentalDiagnosisCNN_train_loss.csv")
val_loss = np.loadtxt("DentalDiagnosisCNN_val_loss.csv")
plt.title("Train vs Validation Error")
n = len(train_err)
plt.plot(range(1,n+1), train_err, label="Train")
plt.plot(range(1,n+1), val_err, label="Validation")
plt.xlabel("Epoch")
plt.ylabel("Error")
plt.legend()
plt.show()
plt.title("Train vs Validation Loss")
plt.plot(range(1,n+1), train_loss, label="Train")
plt.plot(range(1,n+1), val_loss, label="Validation")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.show()

def test_net(model, test_loader, criterion):
    model.eval()
    total_loss = 0.0
    total_err = 0
    total_samples = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            total_loss += loss.item()

            preds = outputs.argmax(dim=1)
            total_err += (preds != labels).sum().item()
            total_samples += len(labels)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    test_err = total_err / total_samples
    test_loss = total_loss / len(test_loader)

    print(f"Test Err: {test_err:.4f}, Test Loss: {test_loss:.4f}")

    # Print the classification report
    print("Test Classification Report:\n")
    print(classification_report(all_labels, all_preds))

    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=set(all_labels), yticklabels=set(all_labels))
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix")
    plt.show()

    cm_normalized = cm.astype('float') / cm.sum(axis=1, keepdims=True)  # Normalize row-wise
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_normalized, annot=True, fmt=".2f", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix (Proportions)")
    plt.show()

test_net(model, test_loader, criterion)

class_names = test_loader.dataset.dataset.classes
print(class_names)