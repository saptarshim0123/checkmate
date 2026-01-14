// API endpoint
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const resumeFileInput = document.getElementById('resumeFile');
const jobDescriptionTextarea = document.getElementById('jobDescription');
const analyzeBtn = document.getElementById('analyzeBtn');
const charCountSpan = document.getElementById('charCount');
const fileInfoDiv = document.getElementById('fileInfo');
const fileNameSpan = document.getElementById('fileName');
const resultsCard = document.getElementById('resultsCard');
const placeholderCard = document.getElementById('placeholderCard');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsContent = document.getElementById('resultsContent');
const errorToast = document.getElementById('errorToast');
const errorMessageSpan = document.getElementById('errorMessage');
const resetBtn = document.getElementById('resetBtn');

// Result display elements
const matchScoreBar = document.getElementById('matchScoreBar');
const matchScoreText = document.getElementById('matchScoreText');
const summaryText = document.getElementById('summaryText');
const technicalGapsList = document.getElementById('technicalGaps');
const softSkillsGapsList = document.getElementById('softSkillsGaps');
const improvedBulletsList = document.getElementById('improvedBullets');
const noTechnicalGaps = document.getElementById('noTechnicalGaps');
const noSoftSkillsGaps = document.getElementById('noSoftSkillsGaps');

// Character count update
jobDescriptionTextarea.addEventListener('input', () => {
    const count = jobDescriptionTextarea.value.length;
    charCountSpan.textContent = count;
    updateAnalyzeButtonState();
});

// File input change handler
resumeFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        if (file.type !== 'application/pdf') {
            showError('Please select a PDF file.');
            resumeFileInput.value = '';
            fileInfoDiv.style.display = 'none';
            updateAnalyzeButtonState();
            return;
        }
        fileNameSpan.textContent = file.name;
        fileInfoDiv.style.display = 'flex';
    } else {
        fileInfoDiv.style.display = 'none';
    }
    updateAnalyzeButtonState();
});

// Update analyze button state
function updateAnalyzeButtonState() {
    const hasFile = resumeFileInput.files.length > 0;
    const hasJD = jobDescriptionTextarea.value.trim().length >= 50;
    analyzeBtn.disabled = !(hasFile && hasJD);
}

// Show error message
function showError(message) {
    errorMessageSpan.textContent = message;
    errorToast.classList.add('show');
    
    setTimeout(() => {
        errorToast.classList.remove('show');
    }, 5000);
}

// Show loading state
function showLoading() {
    loadingSpinner.style.display = 'block';
    resultsContent.style.display = 'none';
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; border-width: 2px; margin: 0;"></div><span>Analyzing...</span>';
}

// Hide loading state
function hideLoading() {
    loadingSpinner.style.display = 'none';
    resultsContent.style.display = 'block';
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = '<i class="bi bi-activity"></i><span>Analyze</span>';
}

// Show results card
function showResults() {
    placeholderCard.style.display = 'none';
    resultsCard.style.display = 'block';
}

// Hide results card
function hideResults() {
    resultsCard.style.display = 'none';
    placeholderCard.style.display = 'block';
}

// Display analysis results
function displayResults(data) {
    const analysis = data.analysis;
    
    // Update match score with animation
    const matchScore = analysis.match_score || 0;
    matchScoreBar.style.width = '0%';
    
    setTimeout(() => {
        matchScoreBar.style.width = `${matchScore}%`;
        matchScoreText.textContent = `${matchScore}%`;
        
        // Update progress bar color based on score
        matchScoreBar.style.background = matchScore >= 70 
            ? 'linear-gradient(90deg, var(--accent-success), #00cc6a)'
            : matchScore >= 40 
            ? 'linear-gradient(90deg, var(--accent-warning), #ff8800)'
            : 'linear-gradient(90deg, var(--accent-error), #cc0000)';
    }, 100);
    
    // Display summary
    summaryText.textContent = analysis.summary || 'No summary available.';
    
    // Display technical gaps
    technicalGapsList.innerHTML = '';
    if (analysis.technical_gap && analysis.technical_gap.length > 0) {
        noTechnicalGaps.style.display = 'none';
        analysis.technical_gap.forEach(gap => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="bi bi-x-circle"></i><span>${gap}</span>`;
            technicalGapsList.appendChild(li);
        });
    } else {
        noTechnicalGaps.style.display = 'flex';
    }
    
    // Display soft skills gaps
    softSkillsGapsList.innerHTML = '';
    if (analysis.soft_skills_gap && analysis.soft_skills_gap.length > 0) {
        noSoftSkillsGaps.style.display = 'none';
        analysis.soft_skills_gap.forEach(gap => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="bi bi-x-circle"></i><span>${gap}</span>`;
            softSkillsGapsList.appendChild(li);
        });
    } else {
        noSoftSkillsGaps.style.display = 'flex';
    }
    
    // Display improved bullet points
    improvedBulletsList.innerHTML = '';
    if (analysis.improved_bullet_points && analysis.improved_bullet_points.length > 0) {
        analysis.improved_bullet_points.forEach((bullet, index) => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="bi bi-check-circle"></i><span><strong>${index + 1}.</strong> ${bullet}</span>`;
            improvedBulletsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.innerHTML = '<span style="color: var(--text-tertiary);">No improvement suggestions available.</span>';
        improvedBulletsList.appendChild(li);
    }
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Analyze button click handler
analyzeBtn.addEventListener('click', async () => {
    const file = resumeFileInput.files[0];
    const jobDescription = jobDescriptionTextarea.value.trim();
    
    if (!file) {
        showError('Please select a PDF file.');
        return;
    }
    
    if (jobDescription.length < 50) {
        showError('Job description must be at least 50 characters long.');
        return;
    }
    
    showLoading();
    showResults();
    
    try {
        const formData = new FormData();
        formData.append('resume', file);
        formData.append('job_description', jobDescription);
        
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            hideLoading();
            displayResults(data);
        } else {
            throw new Error('Analysis failed. Please try again.');
        }
        
    } catch (error) {
        hideLoading();
        showError(error.message || 'An error occurred during analysis. Please try again.');
        console.error('Error:', error);
    }
});

// Reset button click handler
resetBtn.addEventListener('click', () => {
    resumeFileInput.value = '';
    jobDescriptionTextarea.value = '';
    charCountSpan.textContent = '0';
    fileInfoDiv.style.display = 'none';
    hideResults();
    updateAnalyzeButtonState();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Initialize button state
updateAnalyzeButtonState();
