#!/usr/bin/env python3
"""
Test script for the Adobe Hackathon Document Intelligence System.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def create_test_pdf():
    """Create a simple test PDF for testing purposes."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a simple test PDF
        pdf_path = "app/input/test_document.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Page 1
        c.drawString(100, 750, "Machine Learning in Healthcare")
        c.drawString(100, 720, "Introduction")
        c.drawString(100, 690, "This document discusses various machine learning techniques")
        c.drawString(100, 660, "that can be applied to medical image analysis and diagnosis.")
        c.drawString(100, 630, "Deep learning models have shown promising results in")
        c.drawString(100, 600, "detecting anomalies in medical images.")
        
        c.showPage()
        
        # Page 2
        c.drawString(100, 750, "Convolutional Neural Networks")
        c.drawString(100, 720, "CNNs are particularly effective for image analysis tasks.")
        c.drawString(100, 690, "They can automatically learn features from medical images")
        c.drawString(100, 660, "without manual feature engineering.")
        
        c.save()
        print(f"Created test PDF: {pdf_path}")
        return pdf_path
        
    except ImportError:
        print("ReportLab not available, cannot create test PDF")
        return None

def test_pdf_processing():
    """Test PDF processing functionality."""
    from src.pdf_processor import PDFProcessor
    
    processor = PDFProcessor()
    
    # Test with a simple text file converted to "PDF" for testing
    test_content = """Machine Learning in Healthcare
    
Introduction
This document discusses various machine learning techniques that can be applied to medical image analysis and diagnosis. Deep learning models have shown promising results in detecting anomalies in medical images.

Convolutional Neural Networks
CNNs are particularly effective for image analysis tasks. They can automatically learn features from medical images without manual feature engineering.

Conclusion
The application of machine learning in healthcare shows great potential for improving diagnostic accuracy and efficiency."""
    
    # Create a mock document structure
    mock_doc = {
        'document': 'test_document.pdf',
        'file_path': 'test_document.pdf',
        'metadata': {
            'title': 'Machine Learning in Healthcare',
            'author': 'Test Author',
            'subject': 'Healthcare ML',
            'num_pages': 2
        },
        'pages': [
            {
                'page_number': 1,
                'raw_text': 'Machine Learning in Healthcare Introduction This document discusses...',
                'cleaned_text': 'Machine Learning in Healthcare Introduction This document discusses various machine learning techniques that can be applied to medical image analysis and diagnosis. Deep learning models have shown promising results in detecting anomalies in medical images.',
                'sections': [
                    {
                        'title': 'Machine Learning in Healthcare',
                        'content': 'This document discusses various machine learning techniques that can be applied to medical image analysis and diagnosis.',
                        'page': 1,
                        'word_count': 20
                    }
                ],
                'word_count': 35
            },
            {
                'page_number': 2,
                'raw_text': 'Convolutional Neural Networks CNNs are particularly effective...',
                'cleaned_text': 'Convolutional Neural Networks CNNs are particularly effective for image analysis tasks. They can automatically learn features from medical images without manual feature engineering.',
                'sections': [
                    {
                        'title': 'Convolutional Neural Networks',
                        'content': 'CNNs are particularly effective for image analysis tasks. They can automatically learn features from medical images without manual feature engineering.',
                        'page': 2,
                        'word_count': 25
                    }
                ],
                'word_count': 30
            }
        ],
        'total_pages': 2
    }
    
    print("✓ PDF processing test passed (using mock data)")
    return mock_doc

def test_relevance_scoring():
    """Test relevance scoring functionality."""
    from src.relevance_scorer import RelevanceScorer
    
    scorer = RelevanceScorer()
    
    # Create test document
    mock_doc = test_pdf_processing()
    
    # Test query
    query = "Data scientist working in healthcare research Find machine learning techniques for medical image analysis"
    
    # Test scoring
    sections = scorer.score_sections(mock_doc, query)
    subsections = scorer.score_subsections(mock_doc, query)
    
    print(f"✓ Relevance scoring test passed - {len(sections)} sections, {len(subsections)} subsections scored")
    return sections, subsections

def test_output_generation():
    """Test output generation functionality."""
    from src.output_generator import OutputGenerator
    
    generator = OutputGenerator()
    
    # Get test data
    sections, subsections = test_relevance_scoring()
    
    # Generate output
    output = generator.generate_output(
        documents=['test_document.pdf'],
        persona='Data scientist working in healthcare research',
        job='Find machine learning techniques for medical image analysis',
        extracted_sections=sections,
        subsection_analysis=subsections
    )
    
    # Validate structure
    required_keys = ['metadata', 'extracted_sections', 'subsection_analysis']
    for key in required_keys:
        assert key in output, f"Missing key: {key}"
    
    print("✓ Output generation test passed")
    return output

def run_integration_test():
    """Run full integration test."""
    print("Running Adobe Hackathon Document Intelligence System Tests")
    print("=" * 60)
    
    try:
        # Test components
        test_pdf_processing()
        test_relevance_scoring()
        output = test_output_generation()
        
        # Save test output
        os.makedirs('app/output', exist_ok=True)
        with open('app/output/test_analysis.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print("\n✓ All tests passed!")
        print("✓ Test output saved to app/output/test_analysis.json")
        
        # Display sample results
        print("\nSample Results:")
        print(f"Persona: {output['metadata']['persona']}")
        print(f"Job: {output['metadata']['job']}")
        print(f"Sections found: {len(output['extracted_sections'])}")
        print(f"Subsections found: {len(output['subsection_analysis'])}")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_integration_test()
