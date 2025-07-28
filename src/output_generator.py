"""
Output generation module for formatting and saving analysis results.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class OutputGenerator:
    """Handles formatting and generation of output files."""
    
    def __init__(self):
        """Initialize the output generator."""
        pass
    
    def generate_output(
        self,
        documents: List[str],
        persona: str,
        job: str,
        extracted_sections: List[Dict[str, Any]],
        subsection_analysis: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate the complete output structure with enhanced metadata.
        
        Args:
            documents: List of document file paths
            persona: Persona description
            job: Job-to-be-done description
            extracted_sections: List of extracted sections with rankings
            subsection_analysis: List of subsection analysis with refined text
            
        Returns:
            Complete output dictionary matching required format
        """
        # Extract document names from paths
        doc_names = [Path(doc).name for doc in documents]
        
        # Calculate additional metrics
        total_sections = len(extracted_sections)
        total_subsections = len(subsection_analysis)
        unique_docs = len(set(section['document'] for section in extracted_sections))
        avg_sections_per_doc = total_sections / unique_docs if unique_docs > 0 else 0
        
        # Generate enhanced metadata
        metadata = {
            "documents": doc_names,
            "persona": persona,
            "job": job,
            "timestamp": datetime.now().isoformat(),
            "total_documents": len(doc_names),
            "total_sections": total_sections,
            "total_subsections": total_subsections,
            "unique_documents_with_content": unique_docs,
            "avg_sections_per_document": round(avg_sections_per_doc, 2),
            "analysis_quality": {
                "sections_found": total_sections > 0,
                "subsections_found": total_subsections > 0,
                "multi_document_coverage": unique_docs > 1,
                "sufficient_content": total_sections >= 5
            },
            "processing_metadata": {
                "system": "Adobe Hackathon 2025 - Document Intelligence",
                "version": "1.0.0",
                "model_info": {
                    "primary": "TF-IDF + Sentence Transformers",
                    "sentence_model": "all-MiniLM-L6-v2",
                    "fallback": "Keyword similarity"
                }
            }
        }
        
        # Format extracted sections with enhanced information
        formatted_sections = []
        for section in extracted_sections:
            formatted_section = {
                "document": section["document"],
                "page": section["page"],
                "section_title": section["section_title"],
                "importance_rank": section["importance_rank"]
            }
            
            # Add confidence score if available
            if "relevance_score" in section:
                formatted_section["confidence_score"] = round(section["relevance_score"], 3)
            
            formatted_sections.append(formatted_section)
        
        # Format subsection analysis with enhanced information
        formatted_subsections = []
        for subsection in subsection_analysis:
            formatted_subsection = {
                "document": subsection["document"],
                "page": subsection["page"],
                "refined_text": subsection["refined_text"],
                "importance_rank": subsection["importance_rank"]
            }
            
            # Add additional metrics
            if "relevance_score" in subsection:
                formatted_subsection["confidence_score"] = round(subsection["relevance_score"], 3)
            
            # Add text statistics
            text = subsection["refined_text"]
            formatted_subsection["text_stats"] = {
                "word_count": len(text.split()),
                "character_count": len(text),
                "estimated_reading_time_seconds": max(1, len(text.split()) * 0.25)  # ~240 words/minute
            }
            
            formatted_subsections.append(formatted_subsection)
        
        # Create complete output structure
        output = {
            "metadata": metadata,
            "extracted_sections": formatted_sections,
            "subsection_analysis": formatted_subsections,
            "summary_statistics": {
                "top_documents_by_relevance": self._get_top_documents(formatted_sections),
                "content_distribution": self._get_content_distribution(formatted_sections),
                "quality_indicators": {
                    "high_confidence_sections": len([s for s in formatted_sections if s.get("confidence_score", 0) > 0.7]),
                    "diverse_sources": len(set(s["document"] for s in formatted_sections)),
                    "page_coverage": len(set(f"{s['document']}-{s['page']}" for s in formatted_sections))
                }
            }
        }
        
        # Validate output structure
        self._validate_output(output)
        
        return output
    
    def _get_top_documents(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get documents ranked by number of relevant sections."""
        doc_counts = {}
        for section in sections[:10]:  # Top 10 sections only
            doc = section["document"]
            doc_counts[doc] = doc_counts.get(doc, 0) + 1
        
        return [
            {"document": doc, "relevant_sections": count}
            for doc, count in sorted(doc_counts.items(), key=lambda x: x[1], reverse=True)
        ]
    
    def _get_content_distribution(self, sections: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of content across pages."""
        page_counts = {}
        for section in sections:
            page = section["page"]
            page_counts[f"page_{page}"] = page_counts.get(f"page_{page}", 0) + 1
        
        return dict(sorted(page_counts.items()))
    
    def _validate_output(self, output: Dict[str, Any]) -> None:
        """
        Validate that output matches expected format.
        
        Args:
            output: Output dictionary to validate
            
        Raises:
            ValueError: If output format is invalid
        """
        required_keys = ["metadata", "extracted_sections", "subsection_analysis"]
        for key in required_keys:
            if key not in output:
                raise ValueError(f"Missing required key in output: {key}")
        
        # Validate metadata
        metadata = output["metadata"]
        required_metadata_keys = ["documents", "persona", "job", "timestamp"]
        for key in required_metadata_keys:
            if key not in metadata:
                raise ValueError(f"Missing required metadata key: {key}")
        
        # Validate extracted sections
        for i, section in enumerate(output["extracted_sections"]):
            required_section_keys = ["document", "page", "section_title", "importance_rank"]
            for key in required_section_keys:
                if key not in section:
                    raise ValueError(f"Missing key '{key}' in extracted_sections[{i}]")
        
        # Validate subsection analysis
        for i, subsection in enumerate(output["subsection_analysis"]):
            required_subsection_keys = ["document", "page", "refined_text", "importance_rank"]
            for key in required_subsection_keys:
                if key not in subsection:
                    raise ValueError(f"Missing key '{key}' in subsection_analysis[{i}]")
        
        logger.info("Output validation successful")
    
    def save_output(self, output: Dict[str, Any], output_path: str) -> None:
        """
        Save output to JSON file.
        
        Args:
            output: Output dictionary to save
            output_path: Path where to save the file
        """
        try:
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Output saved successfully to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving output to {output_path}: {e}")
            raise
    
    def generate_summary_report(self, output: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary report.
        
        Args:
            output: Output dictionary
            
        Returns:
            Summary report as string
        """
        metadata = output["metadata"]
        sections = output["extracted_sections"]
        subsections = output["subsection_analysis"]
        
        report = []
        report.append("=" * 60)
        report.append("DOCUMENT INTELLIGENCE ANALYSIS SUMMARY")
        report.append("=" * 60)
        report.append("")
        
        # Metadata section
        report.append("ANALYSIS METADATA:")
        report.append(f"  Persona: {metadata['persona']}")
        report.append(f"  Job-to-be-done: {metadata['job']}")
        report.append(f"  Documents analyzed: {metadata['total_documents']}")
        report.append(f"  Timestamp: {metadata['timestamp']}")
        report.append("")
        
        # Documents processed
        report.append("DOCUMENTS PROCESSED:")
        for doc in metadata["documents"]:
            report.append(f"  - {doc}")
        report.append("")
        
        # Top sections
        report.append("TOP RELEVANT SECTIONS:")
        for section in sections[:10]:  # Top 10 sections
            report.append(f"  {section['importance_rank']}. {section['section_title']}")
            report.append(f"     Document: {section['document']}, Page: {section['page']}")
        report.append("")
        
        # Performance summary
        report.append("ANALYSIS STATISTICS:")
        report.append(f"  Total sections extracted: {len(sections)}")
        report.append(f"  Total subsections analyzed: {len(subsections)}")
        report.append("")
        
        return "\n".join(report)
    
    def export_to_csv(self, output: Dict[str, Any], csv_path: str) -> None:
        """
        Export results to CSV format for further analysis.
        
        Args:
            output: Output dictionary
            csv_path: Path to save CSV file
        """
        try:
            import pandas as pd
            
            # Create sections DataFrame
            sections_df = pd.DataFrame(output["extracted_sections"])
            sections_csv_path = csv_path.replace('.csv', '_sections.csv')
            sections_df.to_csv(sections_csv_path, index=False)
            
            # Create subsections DataFrame
            subsections_df = pd.DataFrame(output["subsection_analysis"])
            subsections_csv_path = csv_path.replace('.csv', '_subsections.csv')
            subsections_df.to_csv(subsections_csv_path, index=False)
            
            logger.info(f"CSV exports saved: {sections_csv_path}, {subsections_csv_path}")
            
        except ImportError:
            logger.warning("Pandas not available, skipping CSV export")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    def format_for_display(self, output: Dict[str, Any]) -> str:
        """
        Format output for console display.
        
        Args:
            output: Output dictionary
            
        Returns:
            Formatted string for display
        """
        lines = []
        
        # Header
        lines.append("\n" + "="*50)
        lines.append("DOCUMENT ANALYSIS RESULTS")
        lines.append("="*50)
        
        # Metadata
        metadata = output["metadata"]
        lines.append(f"\nPersona: {metadata['persona']}")
        lines.append(f"Job: {metadata['job']}")
        lines.append(f"Documents: {', '.join(metadata['documents'])}")
        
        # Top sections
        lines.append(f"\nTOP {min(10, len(output['extracted_sections']))} RELEVANT SECTIONS:")
        for section in output["extracted_sections"][:10]:
            lines.append(f"  {section['importance_rank']}. {section['section_title']}")
            lines.append(f"     📄 {section['document']} (Page {section['page']})")
        
        # Top subsections
        lines.append(f"\nTOP {min(5, len(output['subsection_analysis']))} REFINED SUBSECTIONS:")
        for subsection in output["subsection_analysis"][:5]:
            lines.append(f"  {subsection['importance_rank']}. 📄 {subsection['document']} (Page {subsection['page']})")
            # Truncate long text for display
            text = subsection['refined_text']
            if len(text) > 150:
                text = text[:147] + "..."
            lines.append(f"     \"{text}\"")
            lines.append("")
        
        return "\n".join(lines)
