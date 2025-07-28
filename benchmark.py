#!/usr/bin/env python3
"""
Performance testing and benchmarking script for Adobe Hackathon submission.
"""

import time
import psutil
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def create_test_documents():
    """Create multiple test documents for performance testing."""
    documents = {
        "machine_learning_fundamentals.txt": """
Machine Learning Fundamentals in Healthcare

Introduction to Machine Learning
Machine learning has revolutionized many industries, particularly healthcare. 
This document explores fundamental concepts and applications.

Supervised Learning
Supervised learning algorithms learn from labeled training data to make predictions 
on new, unseen data. Common applications include image classification and diagnosis.

Convolutional Neural Networks
CNNs are particularly effective for image analysis tasks. In medical imaging, 
they can detect patterns in X-rays, MRIs, and CT scans with high accuracy.

Transfer Learning
Pre-trained models can be fine-tuned for specific medical tasks, reducing 
training time and improving performance on smaller datasets.

Deep Learning Applications
Deep learning has shown remarkable success in medical image analysis, 
drug discovery, and genomics research.

Computer Vision in Medicine
Computer vision techniques enable automated analysis of medical images, 
supporting radiologists and improving diagnostic accuracy.
        """,
        
        "healthcare_ai_research.txt": """
Artificial Intelligence in Healthcare Research

Executive Summary
AI technologies are transforming healthcare research through advanced 
data analysis and predictive modeling capabilities.

Natural Language Processing
NLP techniques are being applied to electronic health records for 
clinical decision support and automated documentation.

Predictive Analytics
Machine learning models can predict patient outcomes, disease progression, 
and treatment responses using historical data.

Medical Image Analysis
AI-powered image analysis helps detect diseases in radiology, pathology, 
and dermatology with superhuman accuracy in many cases.

Drug Discovery
Machine learning accelerates drug discovery by predicting molecular 
properties and identifying potential therapeutic compounds.

Challenges and Opportunities
Data privacy, regulatory compliance, and clinical integration remain 
key challenges for widespread AI adoption in healthcare.

Future Directions
The future of healthcare AI includes personalized medicine, real-time 
monitoring, and AI-assisted surgical procedures.
        """,
        
        "clinical_decision_support.txt": """
Clinical Decision Support Systems

Overview
Clinical decision support systems (CDSS) provide healthcare professionals 
with patient-specific assessments and evidence-based recommendations.

Machine Learning Integration
Modern CDSS incorporate machine learning algorithms to analyze patient 
data and provide intelligent recommendations.

Diagnostic Assistance
AI-powered diagnostic tools can help identify diseases from symptoms, 
lab results, and medical imaging data.

Treatment Recommendation
Machine learning models can suggest optimal treatment plans based on 
patient characteristics and clinical evidence.

Risk Assessment
Predictive models assess patient risk for various conditions, enabling 
proactive interventions and preventive care.

Quality Improvement
CDSS can help reduce medical errors, improve care quality, and 
standardize treatment protocols across healthcare institutions.

Implementation Challenges
Successful CDSS implementation requires careful consideration of workflow 
integration, user training, and clinical validation.
        """,
        
        "medical_data_science.txt": """
Medical Data Science and Analytics

Data-Driven Healthcare
Healthcare is increasingly becoming data-driven, with electronic health 
records, wearable devices, and genomic data providing rich information.

Big Data Analytics
Big data techniques enable analysis of large-scale healthcare datasets 
to identify patterns and generate insights.

Feature Engineering
Effective feature engineering is crucial for building accurate machine 
learning models from medical data.

Model Validation
Rigorous validation methodologies ensure that medical AI models are 
safe, effective, and generalizable.

Interpretability
Explainable AI techniques help clinicians understand model predictions 
and build trust in AI-assisted decision making.

Regulatory Considerations
Medical AI systems must comply with healthcare regulations and 
demonstrate clinical safety and efficacy.

Ethical AI
Ensuring fairness, transparency, and patient privacy in medical AI 
applications is essential for responsible deployment.
        """,
        
        "imaging_technology_trends.txt": """
Medical Imaging Technology Trends

Advanced Imaging Techniques
New imaging modalities and techniques provide unprecedented views 
into human anatomy and physiology.

AI-Enhanced Imaging
Artificial intelligence enhances image acquisition, reconstruction, 
and analysis across all imaging modalities.

Radiomics and Deep Learning
Radiomics extracts quantitative features from medical images, while 
deep learning automatically learns relevant image patterns.

Real-Time Analysis
AI enables real-time image analysis during procedures, providing 
immediate feedback to healthcare providers.

3D Reconstruction
Advanced 3D reconstruction techniques create detailed anatomical 
models from 2D image slices.

Automated Reporting
Natural language generation creates automated radiology reports 
from image analysis results.

Quality Assurance
AI-powered quality assurance tools ensure consistent image quality 
and detect potential acquisition errors.
        """
    }
    
    # Ensure input directory exists
    input_dir = Path("app/input")
    input_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test documents
    for filename, content in documents.items():
        file_path = input_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
    
    return list(documents.keys())

def run_performance_test(num_documents: int = 5) -> Dict[str, Any]:
    """Run performance test with specified number of documents."""
    from main import main
    
    print(f"\n🔬 Running performance test with {num_documents} documents...")
    
    # Monitor system resources
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    start_time = time.time()
    
    try:
        # Run the main system
        result = main()
        
        # Calculate performance metrics
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        return {
            "success": True,
            "processing_time": processing_time,
            "memory_start_mb": start_memory,
            "memory_end_mb": end_memory,
            "memory_delta_mb": memory_used,
            "documents_processed": num_documents,
            "sections_found": len(result.get("extracted_sections", [])),
            "subsections_found": len(result.get("subsection_analysis", [])),
            "performance_rating": "EXCELLENT" if processing_time < 30 else "GOOD" if processing_time < 60 else "NEEDS_IMPROVEMENT"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "processing_time": time.time() - start_time,
            "memory_delta_mb": process.memory_info().rss / 1024 / 1024 - start_memory
        }

def benchmark_system():
    """Run comprehensive benchmarks."""
    print("🏆 Adobe Hackathon 2025 - Performance Benchmarking")
    print("=" * 60)
    
    # Create test data
    print("📄 Creating test documents...")
    documents = create_test_documents()
    print(f"✅ Created {len(documents)} test documents")
    
    # Test different scenarios
    scenarios = [
        {"name": "Standard Test (5 docs)", "num_docs": 5},
        {"name": "Minimal Test (3 docs)", "num_docs": 3},
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}")
        print("-" * 40)
        
        # Limit documents for this test
        all_files = list(Path("app/input").glob("*.txt"))
        test_files = all_files[:scenario['num_docs']]
        
        # Temporarily move unused files
        temp_files = []
        for file in all_files[scenario['num_docs']:]:
            temp_path = file.with_suffix('.tmp')
            file.rename(temp_path)
            temp_files.append((file, temp_path))
        
        try:
            result = run_performance_test(scenario['num_docs'])
            results.append({"scenario": scenario['name'], **result})
            
            if result['success']:
                print(f"✅ Processing time: {result['processing_time']:.2f}s")
                print(f"💾 Memory usage: {result['memory_delta_mb']:.1f}MB")
                print(f"📑 Sections found: {result['sections_found']}")
                print(f"📝 Subsections found: {result['subsections_found']}")
                print(f"🏆 Rating: {result['performance_rating']}")
                
                # Competition validation
                if result['processing_time'] <= 60:
                    print("✅ SPEED REQUIREMENT MET: ≤60 seconds")
                else:
                    print("❌ SPEED REQUIREMENT FAILED: >60 seconds")
                    
                if result['memory_delta_mb'] < 1000:
                    print("✅ MEMORY REQUIREMENT MET: <1GB")
                else:
                    print("⚠️  MEMORY WARNING: Approaching 1GB limit")
            else:
                print(f"❌ Test failed: {result['error']}")
                
        finally:
            # Restore files
            for original, temp in temp_files:
                temp.rename(original)
    
    # Generate benchmark report
    print("\n📈 BENCHMARK SUMMARY")
    print("=" * 60)
    
    successful_results = [r for r in results if r.get('success', False)]
    
    if successful_results:
        avg_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
        avg_memory = sum(r['memory_delta_mb'] for r in successful_results) / len(successful_results)
        
        print(f"Average processing time: {avg_time:.2f}s")
        print(f"Average memory usage: {avg_memory:.1f}MB")
        print(f"Success rate: {len(successful_results)}/{len(results)} ({len(successful_results)/len(results)*100:.1f}%)")
        
        # Competition compliance
        all_fast = all(r['processing_time'] <= 60 for r in successful_results)
        all_efficient = all(r['memory_delta_mb'] < 1000 for r in successful_results)
        
        print(f"\n🏆 HACKATHON COMPLIANCE:")
        print(f"⏱️  Speed requirement (≤60s): {'✅ PASS' if all_fast else '❌ FAIL'}")
        print(f"💾 Memory requirement (<1GB): {'✅ PASS' if all_efficient else '❌ FAIL'}")
        
        if all_fast and all_efficient:
            print("\n🎉 ALL HACKATHON REQUIREMENTS MET! 🎉")
        else:
            print("\n⚠️  Some requirements not met - optimization needed")
    
    # Save benchmark results
    benchmark_file = "app/output/benchmark_results.json"
    os.makedirs("app/output", exist_ok=True)
    with open(benchmark_file, 'w') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / 1024**3, 2),
                "python_version": sys.version
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n📊 Detailed results saved to: {benchmark_file}")

if __name__ == "__main__":
    benchmark_system()
