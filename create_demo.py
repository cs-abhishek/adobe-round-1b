#!/usr/bin/env python3
"""
Demo script that creates sample PDFs for testing the Document Intelligence System.
"""

import os
import json
from pathlib import Path

def create_sample_text_files():
    """Create sample text files as PDF substitutes for testing."""
    
    # Sample document 1: Machine Learning Research Paper
    doc1_content = """
Deep Learning Applications in Medical Image Analysis

Abstract
This paper explores the application of deep learning techniques in medical image analysis, 
particularly focusing on convolutional neural networks (CNNs) for diagnostic imaging.

Introduction
Medical imaging plays a crucial role in modern healthcare diagnosis and treatment planning. 
Traditional image analysis methods often require manual feature extraction and expert 
interpretation, which can be time-consuming and subject to human error.

Methodology
We implemented several CNN architectures including ResNet, VGG, and custom models 
specifically designed for medical image classification. Our dataset consisted of 
10,000 medical images across different modalities.

Convolutional Neural Networks
CNNs have revolutionized computer vision tasks by automatically learning hierarchical 
features from raw image data. In medical imaging, CNNs can detect patterns that may 
not be visible to the human eye.

Results and Discussion
Our experiments showed that deep learning models achieved 95% accuracy in detecting 
anomalies in chest X-rays and 92% accuracy in MRI scan analysis. These results 
demonstrate the potential of AI in healthcare diagnostics.

Transfer Learning
Pre-trained models on ImageNet showed significant improvement when fine-tuned on 
medical datasets, reducing training time and improving generalization.

Conclusion
Deep learning techniques show tremendous promise for medical image analysis applications. 
Future work should focus on interpretability and clinical integration.
"""

    # Sample document 2: Healthcare Technology Report
    doc2_content = """
Healthcare Technology Trends 2024

Executive Summary
This report analyzes emerging technologies in healthcare, including artificial 
intelligence, telemedicine, and wearable devices.

Artificial Intelligence in Healthcare
AI technologies are transforming healthcare delivery through predictive analytics, 
diagnostic assistance, and personalized treatment recommendations.

Machine Learning Applications
Supervised learning algorithms are being used for disease prediction, while 
unsupervised learning helps in drug discovery and genomic analysis.

Computer Vision in Medicine
Medical imaging analysis using computer vision has shown remarkable progress in 
radiology, pathology, and dermatology applications.

Natural Language Processing
NLP techniques are being applied to electronic health records for clinical decision 
support and automated documentation.

Challenges and Opportunities
Data privacy, regulatory compliance, and integration with existing systems remain 
key challenges for healthcare AI adoption.

Future Outlook
The healthcare AI market is expected to grow significantly, with increased focus on 
precision medicine and remote patient monitoring.
"""

    # Sample document 3: Technical Documentation
    doc3_content = """
Medical Image Processing Toolkit Documentation

Overview
This toolkit provides functions for processing and analyzing medical images using 
machine learning and computer vision techniques.

Image Preprocessing
Functions for noise reduction, contrast enhancement, and image normalization are 
essential for preparing medical images for analysis.

Feature Extraction
The toolkit includes methods for extracting relevant features from medical images, 
including texture analysis and morphological operations.

Classification Algorithms
Support Vector Machines (SVM), Random Forest, and Neural Networks are implemented 
for image classification tasks.

Deep Learning Integration
TensorFlow and PyTorch integrations allow for custom CNN architectures and 
pre-trained model usage.

Performance Metrics
Accuracy, precision, recall, and F1-score calculations are available for model 
evaluation on medical datasets.

API Reference
Detailed documentation of all functions and classes with examples for medical 
image analysis workflows.
"""

    # Create input directory if it doesn't exist
    input_dir = Path("app/input")
    input_dir.mkdir(parents=True, exist_ok=True)
    
    # Save sample documents as text files (simulating PDF content)
    documents = [
        ("medical_ml_research.txt", doc1_content),
        ("healthcare_tech_report.txt", doc2_content),
        ("medical_imaging_toolkit.txt", doc3_content)
    ]
    
    for filename, content in documents:
        file_path = input_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Created sample document: {file_path}")

def create_sample_personas():
    """Create sample persona configurations."""
    personas = [
        {
            "persona": "Data scientist working in healthcare research",
            "job": "Find machine learning techniques and methodologies for medical image analysis and diagnosis"
        },
        {
            "persona": "Medical researcher studying AI applications",
            "job": "Identify computer vision approaches for radiology and diagnostic imaging"
        },
        {
            "persona": "Healthcare technology consultant",
            "job": "Research emerging AI trends and applications in medical practice"
        },
        {
            "persona": "Software engineer developing medical tools",
            "job": "Find technical documentation and implementation details for medical image processing"
        }
    ]
    
    # Save default persona
    with open("app/persona.json", 'w', encoding='utf-8') as f:
        json.dump(personas[0], f, indent=2)
    print("Created default persona configuration")
    
    # Save additional personas for testing
    for i, persona in enumerate(personas[1:], 2):
        filename = f"app/persona_{i}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(persona, f, indent=2)
        print(f"Created additional persona: {filename}")

def create_demo_readme():
    """Create README for demo setup."""
    readme_content = """
# Demo Setup Complete!

This demo has created sample documents and persona configurations for testing the Document Intelligence System.

## Files Created:

### Sample Documents (app/input/):
- `medical_ml_research.txt` - Research paper on deep learning in medical imaging
- `healthcare_tech_report.txt` - Technology trends report
- `medical_imaging_toolkit.txt` - Technical documentation

### Persona Configurations:
- `app/persona.json` - Default: Data scientist in healthcare research
- `app/persona_2.json` - Medical researcher studying AI applications
- `app/persona_3.json` - Healthcare technology consultant
- `app/persona_4.json` - Software engineer developing medical tools

## How to Run Demo:

1. **Basic Demo:**
   ```
   python main.py
   ```

2. **Test Different Personas:**
   ```
   # Copy a different persona configuration
   copy app\\persona_2.json app\\persona.json
   python main.py
   ```

3. **Windows Batch Script:**
   ```
   run.bat
   ```

## Expected Output:

The system will process the sample documents and generate:
- `app/output/analysis.json` - Complete analysis results
- Console output showing processing progress and results

## Performance Notes:

Since these are text files (not PDFs), the processing will be faster than with actual PDF files. The system demonstrates the same analysis logic that would be used with real PDF documents.

To test with real PDFs, simply replace the .txt files in `app/input/` with actual PDF files.
"""
    
    with open("DEMO_README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content.strip())
    print("Created demo README")

def main():
    """Create complete demo setup."""
    print("Creating Demo Setup for Adobe Hackathon Document Intelligence System")
    print("=" * 70)
    
    create_sample_text_files()
    create_sample_personas()
    create_demo_readme()
    
    print("\n" + "=" * 70)
    print("✓ Demo setup complete!")
    print("\nNext steps:")
    print("1. Run: python main.py")
    print("2. Check results in app/output/analysis.json")
    print("3. See DEMO_README.md for more options")

if __name__ == "__main__":
    main()
