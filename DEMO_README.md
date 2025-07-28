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
   copy app\persona_2.json app\persona.json
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