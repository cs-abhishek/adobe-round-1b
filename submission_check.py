#!/usr/bin/env python3
"""
Adobe Hackathon 2025 - Round 1B: Submission Validation
Comprehensive pre-submission checklist and validation
"""

import os
import json
import subprocess
import time
import sys
from pathlib import Path

class SubmissionValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = Path.cwd()
        
    def log_success(self, msg):
        print(f"✅ {msg}")
        
    def log_warning(self, msg):
        print(f"⚠️  {msg}")
        self.warnings.append(msg)
        
    def log_error(self, msg):
        print(f"❌ {msg}")
        self.errors.append(msg)
        
    def log_info(self, msg):
        print(f"ℹ️  {msg}")

    def check_required_files(self):
        """Check all required files are present"""
        print("\n📁 Checking Required Files...")
        
        required_files = [
            'main.py',
            'requirements.txt',
            'Dockerfile',
            'README.md',
            'src/pdf_processor.py',
            'src/text_analyzer.py', 
            'src/relevance_scorer.py',
            'src/output_generator.py'
        ]
        
        for file_path in required_files:
            if (self.project_root / file_path).exists():
                self.log_success(f"Found {file_path}")
            else:
                self.log_error(f"Missing required file: {file_path}")
                
        # Check directories
        required_dirs = ['input', 'output', 'src']
        for dir_path in required_dirs:
            if (self.project_root / dir_path).exists():
                self.log_success(f"Found directory: {dir_path}")
            else:
                self.log_warning(f"Missing directory: {dir_path} (will be created automatically)")

    def check_dependencies(self):
        """Validate requirements.txt and dependencies"""
        print("\n📦 Checking Dependencies...")
        
        req_file = self.project_root / 'requirements.txt'
        if not req_file.exists():
            self.log_error("requirements.txt not found")
            return
            
        with open(req_file, 'r', encoding='utf-8') as f:
            requirements = f.read().strip().split('\n')
            
        # Check for critical dependencies
        critical_deps = ['PyPDF2', 'scikit-learn', 'numpy', 'nltk']
        found_deps = []
        
        for req in requirements:
            if req.strip() and not req.startswith('#'):
                dep_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
                found_deps.append(dep_name.lower())
                
        for dep in critical_deps:
            if dep.lower() in found_deps:
                self.log_success(f"Found critical dependency: {dep}")
            else:
                self.log_error(f"Missing critical dependency: {dep}")
                
        # Check for sentence transformers (optional but recommended)
        if 'sentence-transformers' in found_deps:
            self.log_success("Found sentence-transformers (enhanced AI capability)")
        else:
            self.log_warning("sentence-transformers not found (will use TF-IDF fallback)")

    def check_docker_config(self):
        """Validate Docker configuration"""
        print("\n🐳 Checking Docker Configuration...")
        
        dockerfile = self.project_root / 'Dockerfile'
        if not dockerfile.exists():
            self.log_error("Dockerfile not found")
            return
            
        with open(dockerfile, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check key Docker requirements
        checks = {
            'python:': 'Base Python image',
            'WORKDIR /app': 'Working directory setup',
            'COPY requirements.txt': 'Requirements copy',
            'RUN pip install': 'Dependency installation',
            'USER': 'Non-root user (security)',
            'EXPOSE': 'Port exposure (if needed)',
        }
        
        # Check for CMD or ENTRYPOINT separately
        has_entrypoint = 'CMD' in content or 'ENTRYPOINT' in content
        
        for check, description in checks.items():
            if check in content:
                self.log_success(f"Docker: {description}")
            else:
                if check == 'USER':
                    self.log_warning(f"Docker: {description} not found")
                elif check == 'EXPOSE':
                    self.log_info(f"Docker: {description} not needed for this project")
                else:
                    self.log_error(f"Docker: Missing {description}")
                    
        if has_entrypoint:
            self.log_success("Docker: Container entry point")
        else:
            self.log_error("Docker: Missing container entry point")

    def check_code_quality(self):
        """Basic code quality checks"""
        print("\n🔍 Checking Code Quality...")
        
        main_file = self.project_root / 'main.py'
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for basic structure
            if 'def main(' in content or 'if __name__ == "__main__"' in content:
                self.log_success("main.py has proper entry point")
            else:
                self.log_warning("main.py might be missing proper entry point")
                
            # Check for error handling
            if 'try:' in content and 'except' in content:
                self.log_success("Error handling found in main.py")
            else:
                self.log_warning("Limited error handling in main.py")

    def check_configuration(self):
        """Check configuration files"""
        print("\n⚙️  Checking Configuration...")
        
        # Check for persona.json (example)
        persona_file = self.project_root / 'persona.json'
        if persona_file.exists():
            try:
                with open(persona_file, 'r', encoding='utf-8') as f:
                    persona_data = json.load(f)
                    
                if 'persona' in persona_data and 'job' in persona_data:
                    self.log_success("Valid persona.json configuration")
                else:
                    self.log_warning("persona.json missing required fields")
            except json.JSONDecodeError:
                self.log_error("persona.json is not valid JSON")
        else:
            self.log_info("No persona.json found (will create default)")
            
        # Check config.json if exists
        config_file = self.project_root / 'config.json'
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                self.log_success("Valid config.json")
            except json.JSONDecodeError:
                self.log_error("config.json is not valid JSON")

    def test_basic_functionality(self):
        """Test basic system functionality"""
        print("\n🧪 Testing Basic Functionality...")
        
        try:
            # Test imports
            sys.path.append(str(self.project_root))
            
            # Test main imports
            import main
            self.log_success("main.py imports successfully")
            
            # Test src modules
            from src import pdf_processor, text_analyzer, relevance_scorer, output_generator
            self.log_success("All src modules import successfully")
            
        except ImportError as e:
            self.log_error(f"Import error: {e}")
        except Exception as e:
            self.log_error(f"Error testing functionality: {e}")

    def check_docker_build(self):
        """Test Docker build process"""
        print("\n🔨 Testing Docker Build...")
        
        try:
            # Check if Docker is available
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_success(f"Docker available: {result.stdout.strip()}")
                
                # Test build (dry run)
                self.log_info("Testing Docker build (this may take a few minutes)...")
                build_result = subprocess.run(['docker', 'build', '-t', 'adobe-hackathon-test', '.'], 
                                            capture_output=True, text=True, timeout=300)
                
                if build_result.returncode == 0:
                    self.log_success("Docker build successful")
                    
                    # Clean up test image
                    subprocess.run(['docker', 'rmi', 'adobe-hackathon-test'], 
                                 capture_output=True)
                else:
                    self.log_error(f"Docker build failed: {build_result.stderr}")
                    
            else:
                self.log_warning("Docker not available for testing")
                
        except subprocess.TimeoutExpired:
            self.log_error("Docker build timed out (>5 minutes)")
        except FileNotFoundError:
            self.log_warning("Docker not installed or not in PATH")
        except Exception as e:
            self.log_warning(f"Could not test Docker build: {e}")

    def check_performance_requirements(self):
        """Check if performance requirements can be met"""
        print("\n⚡ Checking Performance Requirements...")
        
        # Check system resources
        try:
            import psutil
            
            cpu_count = psutil.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            self.log_info(f"System: {cpu_count} CPU cores, {memory_gb:.1f}GB RAM")
            
            if cpu_count >= 2:
                self.log_success("Sufficient CPU cores for processing")
            else:
                self.log_warning("Limited CPU cores may affect performance")
                
            if memory_gb >= 2:
                self.log_success("Sufficient memory for processing")
            else:
                self.log_warning("Limited memory may affect performance")
                
        except ImportError:
            self.log_info("psutil not available for system check")

    def generate_report(self):
        """Generate final validation report"""
        print("\n" + "="*50)
        print("🏆 Adobe Hackathon Round 1B - Submission Validation Report")
        print("="*50)
        
        if not self.errors:
            print("✅ VALIDATION PASSED - Ready for submission!")
        else:
            print("❌ VALIDATION FAILED - Issues must be resolved")
            
        print(f"\n📊 Summary:")
        print(f"   ✅ Passed checks: {len([]) if self.errors else 'All'}")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")
        print(f"   ❌ Errors: {len(self.errors)}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings to address:")
            for warning in self.warnings:
                print(f"   • {warning}")
                
        if self.errors:
            print(f"\n❌ Critical errors to fix:")
            for error in self.errors:
                print(f"   • {error}")
                
        print(f"\n🚀 Next steps:")
        if not self.errors:
            print("   1. Run final Docker test: ./test_docker.sh")
            print("   2. Prepare submission package")
            print("   3. Submit to Adobe Hackathon!")
        else:
            print("   1. Fix all critical errors above")
            print("   2. Re-run validation: python submission_check.py")
            print("   3. Test Docker deployment")

def main():
    print("🏆 Adobe Hackathon 2025 - Round 1B")
    print("📋 Submission Validation Tool")
    print("="*50)
    
    validator = SubmissionValidator()
    
    # Run all checks
    validator.check_required_files()
    validator.check_dependencies()
    validator.check_docker_config()
    validator.check_configuration()
    validator.check_code_quality()
    validator.test_basic_functionality()
    validator.check_performance_requirements()
    validator.check_docker_build()
    
    # Generate report
    validator.generate_report()
    
    # Exit with appropriate code
    return 0 if not validator.errors else 1

if __name__ == "__main__":
    sys.exit(main())
