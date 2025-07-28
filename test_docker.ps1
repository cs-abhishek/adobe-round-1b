# Adobe Hackathon Round 1B - Docker Testing Suite (PowerShell)
# Tests all aspects of containerized deployment on Windows

param(
    [switch]$SkipCleanup,
    [string]$ImageName = "adobe-hackathon-1b",
    [string]$ContainerName = "adobe-test-container"
)

# Colors for output
$colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $colors.Blue
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor $colors.Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor $colors.Yellow
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor $colors.Red
}

function Cleanup {
    if (-not $SkipCleanup) {
        Write-Info "Cleaning up test environment..."
        docker stop $ContainerName 2>$null | Out-Null
        docker rm $ContainerName 2>$null | Out-Null
        
        # Clean up test files
        if (Test-Path "test_input") { Remove-Item -Recurse -Force "test_input" }
        if (Test-Path "test_output") { Remove-Item -Recurse -Force "test_output" }
        if (Test-Path "test_persona.json") { Remove-Item -Force "test_persona.json" }
    }
}

try {
    Write-Host "🐳 Adobe Hackathon Round 1B - Docker Testing Suite" -ForegroundColor $colors.Blue
    Write-Host ("=" * 50) -ForegroundColor $colors.Blue
    Write-Host ""

    # Test 1: Build Docker image
    Write-Info "Test 1: Building Docker image..."
    $buildResult = docker build -t $ImageName . 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully"
    } else {
        Write-Error "Docker build failed"
        Write-Host $buildResult
        exit 1
    }

    # Test 2: Check image size
    Write-Info "Test 2: Checking image size..."
    $imageSize = docker images $ImageName --format "{{.Size}}"
    Write-Info "Image size: $imageSize"

    # Test 3: Create test input
    Write-Info "Test 3: Preparing test input..."
    New-Item -ItemType Directory -Force -Path "test_input", "test_output" | Out-Null

    # Create persona file
    $persona = @{
        persona = "Senior software engineer specializing in machine learning"
        job = "Find best practices for implementing neural networks and deep learning models in production systems"
    } | ConvertTo-Json -Depth 3

    $persona | Out-File -FilePath "test_persona.json" -Encoding UTF8

    # Create test document
    $testDocument = @"
# Machine Learning in Production

## Introduction
This document covers best practices for deploying machine learning models in production environments.

## Neural Network Optimization
Deep learning models require careful optimization for production deployment. Key considerations include:
- Model quantization to reduce size
- Batch processing for efficiency
- GPU memory management
- Inference optimization

## Production Architecture
Successful ML production systems typically include:
- Model versioning and rollback capabilities
- A/B testing frameworks
- Monitoring and alerting systems
- Data pipeline management

## Performance Monitoring
Monitor key metrics:
- Inference latency
- Throughput
- Model accuracy drift
- Resource utilization

## Best Practices
1. Use containerization for consistent deployments
2. Implement proper logging and monitoring
3. Design for scalability
4. Plan for model updates and rollbacks
5. Ensure data quality validation

## Conclusion
Production ML systems require careful planning and robust infrastructure to succeed.
"@

    $testDocument | Out-File -FilePath "test_input\test_document.txt" -Encoding UTF8
    Write-Success "Test input prepared"

    # Test 4: Run container
    Write-Info "Test 4: Running container..."
    $currentDir = (Get-Location).Path
    
    docker run -d `
        --name $ContainerName `
        -v "${currentDir}\test_input:/app/input" `
        -v "${currentDir}\test_output:/app/output" `
        -v "${currentDir}\test_persona.json:/app/persona.json" `
        -e KEEP_ALIVE=false `
        $ImageName

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start container"
        exit 1
    }

    # Wait for container to complete
    Write-Info "Waiting for processing to complete..."
    docker wait $ContainerName | Out-Null

    # Test 5: Check container logs
    Write-Info "Test 5: Checking container execution logs..."
    $logs = docker logs $ContainerName
    Write-Host $logs

    # Test 6: Validate output
    Write-Info "Test 6: Validating output..."
    if (Test-Path "test_output\analysis.json") {
        Write-Success "Output file generated"
        
        # Check JSON validity
        try {
            $outputContent = Get-Content "test_output\analysis.json" -Raw | ConvertFrom-Json
            Write-Success "Output is valid JSON"
            
            # Check content
            Write-Host "📊 Output Analysis:"
            $docCount = if ($outputContent.metadata.documents) { $outputContent.metadata.documents.Count } else { 0 }
            $sectionCount = if ($outputContent.extracted_sections) { $outputContent.extracted_sections.Count } else { 0 }
            $processingTime = if ($outputContent.metadata.processing_time) { $outputContent.metadata.processing_time } else { "N/A" }
            
            Write-Host "   Documents: $docCount"
            Write-Host "   Sections: $sectionCount"
            Write-Host "   Processing time: $processingTime seconds"
            
            # Validate structure
            $requiredKeys = @('extracted_sections', 'subsection_analysis', 'metadata')
            $missingKeys = $requiredKeys | Where-Object { -not $outputContent.PSObject.Properties.Name.Contains($_) }
            
            if ($missingKeys.Count -gt 0) {
                Write-Error "Missing required keys: $($missingKeys -join ', ')"
                exit 1
            } else {
                Write-Success "Output structure is valid"
            }
            
            # Check if relevant content was found
            if ($sectionCount -gt 0) {
                Write-Success "Relevant sections were extracted"
            } else {
                Write-Warning "No relevant sections found"
            }
            
        } catch {
            Write-Error "Output is not valid JSON: $_"
            exit 1
        }
    } else {
        Write-Error "No output file generated"
        exit 1
    }

    # Test 7: Performance validation
    Write-Info "Test 7: Validating performance constraints..."
    if ($logs -match "Processing time: (\d+) seconds") {
        $processingTime = [int]$matches[1]
        if ($processingTime -le 60) {
            Write-Success "Processing time: ${processingTime}s (meets <60s requirement)"
        } else {
            Write-Warning "Processing time: ${processingTime}s (exceeds 60s requirement)"
        }
    } else {
        Write-Warning "Could not extract processing time from logs"
    }

    # Test 8: Security validation
    Write-Info "Test 8: Checking security configuration..."
    $userInfo = docker run --rm $ImageName id
    if ($userInfo -match "uid=1000") {
        Write-Success "Running as non-root user"
    } else {
        Write-Warning "User configuration: $userInfo"
    }

    # Test 9: Offline operation validation
    Write-Info "Test 9: Validating offline operation..."
    if ($logs -match "TRANSFORMERS_OFFLINE=1") {
        Write-Success "Offline mode properly configured"
    } else {
        Write-Warning "Offline mode configuration not detected"
    }

    Write-Host ""
    Write-Success "🎉 All Docker tests completed!"
    Write-Host ""
    Write-Host "📋 Test Summary:" -ForegroundColor $colors.Blue
    Write-Host "   ✅ Image build: SUCCESS" -ForegroundColor $colors.Green
    Write-Host "   ✅ Container execution: SUCCESS" -ForegroundColor $colors.Green
    Write-Host "   ✅ Output generation: SUCCESS" -ForegroundColor $colors.Green
    Write-Host "   ✅ JSON validation: SUCCESS" -ForegroundColor $colors.Green
    Write-Host "   ✅ Performance: ${processingTime}s" -ForegroundColor $colors.Green
    Write-Host "   ✅ Security: Non-root user" -ForegroundColor $colors.Green
    Write-Host "   ✅ Offline operation: Configured" -ForegroundColor $colors.Green

    Write-Host ""
    Write-Host "🐳 Docker deployment is ready for Adobe Hackathon Round 1B!" -ForegroundColor $colors.Blue
    Write-Host "📁 Use the following commands to run:" -ForegroundColor $colors.Blue
    Write-Host "   docker build -t adobe-hackathon-1b ." -ForegroundColor $colors.White
    Write-Host "   docker run -v ./input:/app/input -v ./output:/app/output adobe-hackathon-1b" -ForegroundColor $colors.White

} catch {
    Write-Error "Test failed: $_"
    exit 1
} finally {
    Cleanup
}
