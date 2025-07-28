#!/usr/bin/env python3
"""
Adobe Hackathon 2025 - Round 1B: Persona-Driven Document Intelligence
Main entry point for the document analysis system.

🏆 Competition Features:
- CPU-only processing (amd64)
- Offline operation (no web calls)
- Model size ≤ 1GB
- Process 3-5 PDFs in <60 seconds
- Persona-driven content extraction
"""

import os
import json
import time
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.pdf_processor import PDFProcessor
from src.text_analyzer import TextAnalyzer
from src.relevance_scorer import RelevanceScorer
from src.output_generator import OutputGenerator

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/hackathon.log', 'a') if os.path.exists('logs') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance during processing."""
    
    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.peak_memory = 0
        
    def start(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.start_memory
        
    def update(self):
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = max(self.peak_memory, current_memory)
        
    def get_stats(self):
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            'processing_time': elapsed,
            'memory_start_mb': self.start_memory,
            'memory_peak_mb': self.peak_memory,
            'memory_delta_mb': self.peak_memory - self.start_memory if self.start_memory else 0
        }

def load_persona_config(persona_path: str) -> Dict[str, str]:
    """Load persona and job configuration from JSON file."""
    try:
        with open(persona_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'persona' not in config or 'job' not in config:
            raise ValueError("persona.json must contain 'persona' and 'job' fields")
        
        return config
    except Exception as e:
        logger.error(f"Error loading persona config: {e}")
        raise

def get_input_pdfs(input_dir: str) -> List[str]:
    """Get list of PDF and text files from input directory."""
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Look for both PDF and text files (text files for demo purposes)
    pdf_files = list(input_path.glob("*.pdf"))
    txt_files = list(input_path.glob("*.txt"))
    
    all_files = pdf_files + txt_files
    
    if not all_files:
        raise ValueError(f"No PDF or text files found in {input_dir}")
    
    if len(all_files) > 10:
        logger.warning(f"Found {len(all_files)} files, but maximum is 10. Using first 10.")
        all_files = all_files[:10]
    
    return [str(f) for f in all_files]

def main():
    """Main execution function."""
    start_time = time.time()
    
    # Define paths
    input_dir = "/app/input"
    persona_path = "/app/persona.json"
    output_dir = "/app/output"
    output_path = "/app/output/analysis.json"
    
    # For development/testing, use relative paths if absolute paths don't exist
    if not os.path.exists(input_dir):
        input_dir = "app/input"
        persona_path = "app/persona.json"
        output_dir = "app/output"
        output_path = "app/output/analysis.json"
    
    try:
        logger.info("Starting Adobe Hackathon Document Intelligence System")
        
        # Load persona configuration
        logger.info("Loading persona configuration...")
        persona_config = load_persona_config(persona_path)
        logger.info(f"Persona: {persona_config['persona']}")
        logger.info(f"Job: {persona_config['job']}")
        
        # Get input PDFs
        logger.info("Scanning for input documents...")
        pdf_files = get_input_pdfs(input_dir)
        logger.info(f"Found {len(pdf_files)} document files to process")
        
        # Initialize components
        logger.info("Initializing processing components...")
        pdf_processor = PDFProcessor()
        text_analyzer = TextAnalyzer()
        relevance_scorer = RelevanceScorer()
        output_generator = OutputGenerator()
        
        # Fit relevance scorer on all documents first
        logger.info("Fitting relevance scorer...")
        try:
            # Quick pass to extract all text for TF-IDF fitting
            all_docs_for_fitting = []
            for pdf_path in pdf_files:
                try:
                    doc_data = pdf_processor.process_pdf(pdf_path)
                    all_docs_for_fitting.append(doc_data)
                except Exception as e:
                    logger.warning(f"Could not process {pdf_path} for fitting: {e}")
            
            if all_docs_for_fitting:
                relevance_scorer.fit_corpus(all_docs_for_fitting)
        except Exception as e:
            logger.warning(f"Could not fit relevance scorer: {e}")
            logger.info("Continuing with individual document processing...")
        
        # Process PDFs
        logger.info("Processing document files...")
        all_documents = []
        for pdf_path in pdf_files:
            logger.info(f"Processing: {os.path.basename(pdf_path)}")
            doc_data = pdf_processor.process_pdf(pdf_path)
            all_documents.append(doc_data)
        
        # Analyze text and score relevance
        logger.info("Analyzing text relevance...")
        query_text = f"{persona_config['persona']} {persona_config['job']}"
        
        extracted_sections = []
        subsection_analysis = []
        
        for doc_data in all_documents:
            # Score and rank sections
            sections = relevance_scorer.score_sections(
                doc_data, query_text
            )
            extracted_sections.extend(sections)
            
            # Analyze subsections
            subsections = relevance_scorer.score_subsections(
                doc_data, query_text
            )
            subsection_analysis.extend(subsections)
        
        # Sort by importance rank
        extracted_sections.sort(key=lambda x: x['importance_rank'])
        subsection_analysis.sort(key=lambda x: x['importance_rank'])
        
        # Generate output
        logger.info("Generating output...")
        os.makedirs(output_dir, exist_ok=True)
        
        output_data = output_generator.generate_output(
            documents=pdf_files,
            persona=persona_config['persona'],
            job=persona_config['job'],
            extracted_sections=extracted_sections,
            subsection_analysis=subsection_analysis
        )
        
        # Save results
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Performance metrics
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"Processing completed successfully!")
        logger.info(f"Total processing time: {processing_time:.2f} seconds")
        logger.info(f"Documents processed: {len(pdf_files)}")
        logger.info(f"Sections extracted: {len(extracted_sections)}")
        logger.info(f"Subsections analyzed: {len(subsection_analysis)}")
        logger.info(f"Output saved to: {output_path}")
        
        if processing_time > 60:
            logger.warning(f"Processing took {processing_time:.2f}s, exceeding 60s target")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()
