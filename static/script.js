// script.js - Main JavaScript for PixelForensics web application
// Page References
const landing = document.getElementById('landing');
const dashboard = document.getElementById('dashboard');
const scanPage = document.getElementById('scan');
const historyPage = document.getElementById('history');
const feedbackPage = document.getElementById('feedback');

// Landing page buttons
document.getElementById('go-scan').onclick = () => showPage(scanPage);
document.getElementById('go-history').onclick = () => showPage(historyPage);

// Navbar navigation
document.getElementById('nav-dashboard').onclick = () => showPage(dashboard);
document.getElementById('nav-scan').onclick = () => showPage(scanPage);
document.getElementById('nav-history').onclick = () => showPage(historyPage);
document.getElementById('nav-feedback').onclick = () => showPage(feedbackPage);

function showPage(page) {
  [landing, dashboard, scanPage, historyPage, feedbackPage].forEach(p =>
    p.classList.add('hidden')
  );
  page.classList.remove('hidden');
}

// File Upload
const dropArea = document.getElementById('drop-area');
const fileElem = document.getElementById('fileElem');
let filesToScan = [];
let currentImagePreview = null;

// Handle click on drop area (but not on file input)
dropArea.addEventListener('click', (e) => {
  if (e.target !== fileElem) {
    fileElem.click();
  }
});

// Handle file selection
fileElem.addEventListener('change', (e) => {
  filesToScan = Array.from(e.target.files);
  if (filesToScan.length > 0) {
    displayImageInDropArea(filesToScan[0]);
  }
});

// Prevent file input from bubbling click to drop area
fileElem.addEventListener('click', (e) => {
  e.stopPropagation();
});

// Handle drag and drop
dropArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropArea.style.borderColor = '#FF007F';
});

dropArea.addEventListener('dragleave', () => {
  dropArea.style.borderColor = '#0FF0FC';
});

dropArea.addEventListener('drop', (e) => {
  e.preventDefault();
  dropArea.style.borderColor = '#0FF0FC';
  filesToScan = Array.from(e.dataTransfer.files);
  if (filesToScan.length > 0) {
    displayImageInDropArea(filesToScan[0]);
  }
});

// Display image preview in drop area
function displayImageInDropArea(file) {
  // Remove existing preview if any
  if (currentImagePreview) {
    currentImagePreview.remove();
  }

  // Hide the default text and file input
  const textElement = dropArea.querySelector('p');
  textElement.style.display = 'none';
  fileElem.style.display = 'none';

  if (file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = document.createElement('img');
      img.src = e.target.result;
      img.alt = file.name;
      img.style.maxWidth = '100%';
      img.style.maxHeight = '250px';
      img.style.objectFit = 'contain';
      img.style.borderRadius = '8px';
      img.style.display = 'block';
      img.style.margin = '0 auto';
      currentImagePreview = img;
      dropArea.appendChild(img);
    };
    reader.readAsDataURL(file);
  } else if (file.type.startsWith('video/')) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const video = document.createElement('video');
      video.src = e.target.result;
      video.controls = true;
      video.style.maxWidth = '100%';
      video.style.maxHeight = '250px';
      video.style.objectFit = 'contain';
      video.style.borderRadius = '8px';
      video.style.display = 'block';
      video.style.margin = '0 auto';
      currentImagePreview = video;
      dropArea.appendChild(video);
    };
    reader.readAsDataURL(file);
  }
}

// Start Scan - NOW CALLS BACKEND API
document.getElementById('startScan').onclick = async () => {
  if (filesToScan.length === 0) {
    alert('Please select files first!');
    return;
  }

  const resultsDiv = document.getElementById('scan-results');
  resultsDiv.innerHTML = '<p style="color: #0FF0FC;">🔄 Analyzing...</p>';
  
  const tbody = document.querySelector('#history-table tbody');

  // Process each file
  for (const file of filesToScan) {
    try {
      // Create FormData to send file to backend
      const formData = new FormData();
      
      if (file.type.startsWith('image/')) {
        formData.append('image', file);
      } else if (file.type.startsWith('video/')) {
        formData.append('video', file);
      } else {
        console.error('Unsupported file type:', file.type);
        continue;
      }

      // Call backend API
      console.log('Sending file to backend:', file.name);
      const response = await fetch('http://localhost:5000/detect-deepfake', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result = await response.json();
      console.log('Backend response:', result);

      // Extract results
      const isDeepfake = result.is_deepfake;
      const confidence = result.confidence;
      const status = isDeepfake ? 'Suspicious' : 'Safe';

      // Clear loading message
      resultsDiv.innerHTML = '';

      // Display scan results below the drop area
      const resultText = document.createElement('div');
      resultText.style.marginTop = '0.8rem';
      resultText.style.padding = '0.8rem';
      resultText.style.backgroundColor = status === 'Safe' ? '#00330022' : '#330000';
      resultText.style.border = `2px solid ${status === 'Safe' ? '#00FF00' : '#FF0000'}`;
      resultText.style.borderRadius = '8px';
      resultText.innerHTML = `
        <h4 style="margin: 0 0 0.5rem 0; font-size: 1rem;">${file.name}</h4>
        <p style="margin: 0.3rem 0; font-size: 0.9rem;"><strong>Status:</strong> ${status} | <strong>Confidence:</strong> ${confidence}%</p>
        <button onclick="downloadReport('${file.name}', '${status}', ${confidence})" style="margin-top: 0.5rem; padding: 0.5rem 1rem; font-size: 0.9rem;">Download Report</button>
      `;
      resultsDiv.appendChild(resultText);

      // Add to History Table
      const row = tbody.insertRow();
      row.innerHTML = `<td>${file.name}</td>
                       <td>${status}</td>
                       <td>${confidence}%</td>
                       <td><button onclick="downloadReport('${file.name}', '${status}', ${confidence})">PDF</button></td>`;

    } catch (error) {
      console.error('Error analyzing file:', file.name, error);
      resultsDiv.innerHTML = `<p style="color: #FF0000;">❌ Error: ${error.message}</p>`;
    }
  }

  // Update Dashboard stats
  document.getElementById('total-scans').textContent = tbody.rows.length;
  document.getElementById('suspicious-scans').textContent = [...tbody.rows].filter(r => r.cells[1].innerText === 'Suspicious').length;
  document.getElementById('safe-scans').textContent = [...tbody.rows].filter(r => r.cells[1].innerText === 'Safe').length;
};

// PDF Report Generation
async function downloadReport(filename, status, score) {
  try {
    // Show loading indicator
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = '⏳ Generating...';
    button.disabled = true;
    
    // Call backend API to generate comprehensive PDF report
    const response = await fetch('http://localhost:5000/api/generate-report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filename: filename
      })
    });
    
    if (!response.ok) {
      throw new Error(`Report generation failed: ${response.status}`);
    }
    
    // Get the PDF blob
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PixelForensics_Report_${filename.replace(/\.[^/.]+$/, '')}.pdf`;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    // Reset button
    button.textContent = originalText;
    button.disabled = false;
    
    console.log('✅ Report downloaded successfully');
    
  } catch (error) {
    console.error('Report download error:', error);
    alert(`Failed to generate report: ${error.message}`);
    
    // Reset button on error
    if (event && event.target) {
      event.target.textContent = 'Download Report';
      event.target.disabled = false;
    }
  }
}

// -----------------------------
// Feedback Submit Logic
// -----------------------------
document.getElementById('submit-feedback').onclick = () => {
  const name = document.getElementById('fb-name').value.trim();
  const msg = document.getElementById('fb-message').value.trim();
  const status = document.getElementById('fb-status');

  if (!name || !msg) {
    status.textContent = "Please fill in all fields.";
    status.style.color = "red";
    return;
  }

  // Mock saving feedback
  status.textContent = "Thank you! Your feedback has been submitted.";
  status.style.color = "lightgreen";

  // Clear fields
  document.getElementById('fb-name').value = "";
  document.getElementById('fb-message').value = "";
};

// Theme Toggle
const themeToggle = document.getElementById('theme-toggle');

themeToggle.onclick = () => {
  document.body.classList.toggle('light-theme');

  if (document.body.classList.contains('light-theme')) {
    themeToggle.textContent = '🌙 Dark Mode';
  } else {
    themeToggle.textContent = '☀️ Light Mode';
  }
};