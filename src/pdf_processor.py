"""
PDF processing module for extracting text and metadata from PDF files.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not installed. Install with: pip install PyPDF2")
    raise

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and page-level processing."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.processed_docs = {}
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF file and extract text with metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing document data with pages and metadata
        """
        doc_name = Path(pdf_path).name
        logger.info(f"Processing document: {doc_name}")
        
        # Handle text files for demo purposes
        if pdf_path.endswith('.txt'):
            return self._process_text_file(pdf_path)
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'title': self._extract_metadata_field(pdf_reader, 'title'),
                    'author': self._extract_metadata_field(pdf_reader, 'author'),
                    'subject': self._extract_metadata_field(pdf_reader, 'subject'),
                    'num_pages': len(pdf_reader.pages)
                }
                
                # Extract text from each page
                pages = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        cleaned_text = self._clean_text(text)
                        
                        # Extract sections from page
                        sections = self._extract_sections(cleaned_text, page_num)
                        
                        page_data = {
                            'page_number': page_num,
                            'raw_text': text,
                            'cleaned_text': cleaned_text,
                            'sections': sections,
                            'word_count': len(cleaned_text.split())
                        }
                        pages.append(page_data)
                        
                    except Exception as e:
                        logger.warning(f"Error processing page {page_num} of {doc_name}: {e}")
                        # Add empty page data to maintain page numbering
                        pages.append({
                            'page_number': page_num,
                            'raw_text': '',
                            'cleaned_text': '',
                            'sections': [],
                            'word_count': 0
                        })
                
                doc_data = {
                    'document': doc_name,
                    'file_path': pdf_path,
                    'metadata': metadata,
                    'pages': pages,
                    'total_pages': len(pages)
                }
                
                self.processed_docs[doc_name] = doc_data
                logger.info(f"Successfully processed {doc_name}: {len(pages)} pages")
                
                return doc_data
                
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise
    
    def _process_text_file(self, text_path: str) -> Dict[str, Any]:
        """
        Process a text file for demo purposes.
        
        Args:
            text_path: Path to the text file
            
        Returns:
            Dictionary containing document data with pages and metadata
        """
        doc_name = Path(text_path).name
        
        try:
            with open(text_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            cleaned_text = self._clean_text(text)
            
            # Split text into artificial "pages" for demo
            words = cleaned_text.split()
            words_per_page = 300  # Simulate ~300 words per page
            
            pages = []
            for page_num in range(1, (len(words) // words_per_page) + 2):
                start_idx = (page_num - 1) * words_per_page
                end_idx = min(page_num * words_per_page, len(words))
                
                if start_idx >= len(words):
                    break
                
                page_text = ' '.join(words[start_idx:end_idx])
                sections = self._extract_sections(page_text, page_num)
                
                page_data = {
                    'page_number': page_num,
                    'raw_text': page_text,
                    'cleaned_text': page_text,
                    'sections': sections,
                    'word_count': len(page_text.split())
                }
                pages.append(page_data)
            
            # Create metadata
            metadata = {
                'title': doc_name.replace('.txt', '').replace('_', ' ').title(),
                'author': 'Demo Author',
                'subject': 'Demo Document',
                'num_pages': len(pages)
            }
            
            doc_data = {
                'document': doc_name,
                'file_path': text_path,
                'metadata': metadata,
                'pages': pages,
                'total_pages': len(pages)
            }
            
            self.processed_docs[doc_name] = doc_data
            logger.info(f"Successfully processed text file {doc_name}: {len(pages)} pages")
            
            return doc_data
            
        except Exception as e:
            logger.error(f"Error processing text file {text_path}: {e}")
            raise
    
    def _extract_metadata_field(self, pdf_reader: PyPDF2.PdfReader, field: str) -> Optional[str]:
        """Extract a specific metadata field from PDF."""
        try:
            if pdf_reader.metadata and hasattr(pdf_reader.metadata, field):
                value = getattr(pdf_reader.metadata, field)
                return str(value) if value else None
        except:
            pass
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\-.,;:!?()[\]{}"\']', ' ', text)
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Strip and return
        return text.strip()
    
    def _extract_sections(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Extract sections from page text based on headers and structure."""
        sections = []
        
        if not text:
            return sections
        
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        current_section = None
        current_content = []
        
        for para in paragraphs:
            # Check if paragraph looks like a header/title
            if self._is_likely_header(para):
                # Save previous section if exists
                if current_section and current_content:
                    sections.append({
                        'title': current_section,
                        'content': ' '.join(current_content),
                        'page': page_num,
                        'word_count': len(' '.join(current_content).split())
                    })
                
                # Start new section
                current_section = para
                current_content = []
            else:
                # Add to current section content
                if current_section:
                    current_content.append(para)
                else:
                    # Text without header - create a generic section
                    if not sections:
                        current_section = f"Content from page {page_num}"
                        current_content = [para]
        
        # Add final section
        if current_section and current_content:
            sections.append({
                'title': current_section,
                'content': ' '.join(current_content),
                'page': page_num,
                'word_count': len(' '.join(current_content).split())
            })
        
        # If no sections were found, create a default one
        if not sections and text:
            sections.append({
                'title': f"Content from page {page_num}",
                'content': text,
                'page': page_num,
                'word_count': len(text.split())
            })
        
        return sections
    
    def _is_likely_header(self, text: str) -> bool:
        """Determine if text is likely a section header."""
        if len(text) > 100:  # Too long to be a header
            return False
        
        # Check for common header patterns
        header_patterns = [
            r'^\d+\.',  # Numbered sections (1., 2., etc.)
            r'^\d+\.\d+',  # Subsections (1.1, 1.2, etc.)
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:?$',  # Title Case
            r'^(Chapter|Section|Part|Introduction|Conclusion)',  # Common headers
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, text):
                return True
        
        # Check if text ends with colon (common for headers)
        if text.endswith(':') and len(text.split()) <= 8:
            return True
        
        # Check if text is short and doesn't end with period
        if len(text.split()) <= 6 and not text.endswith('.'):
            return True
        
        return False
    
    def get_all_text(self, doc_data: Dict[str, Any]) -> str:
        """Get all text content from a document."""
        all_text = []
        for page in doc_data['pages']:
            if page['cleaned_text']:
                all_text.append(page['cleaned_text'])
        return ' '.join(all_text)
    
    def get_page_text(self, doc_data: Dict[str, Any], page_num: int) -> str:
        """Get text from a specific page."""
        for page in doc_data['pages']:
            if page['page_number'] == page_num:
                return page['cleaned_text']
        return ""
