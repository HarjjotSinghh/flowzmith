// Main JavaScript for Flowzmith

// Global variables
let socket = null;
let currentSubmissionId = null;

// Initialize WebSocket connection
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    socket = new WebSocket(wsUrl);

    socket.onopen = function(event) {
        console.log('WebSocket connection established');
        showNotification('Connected to real-time updates', 'success');
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    socket.onclose = function(event) {
        console.log('WebSocket connection closed');
        showNotification('Disconnected from real-time updates', 'warning');
        // Attempt to reconnect after 5 seconds
        setTimeout(initWebSocket, 5000);
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
        showNotification('Connection error', 'danger');
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'submission_update':
            updateSubmissionStatus(data.submission_id, data.status, data.message);
            break;
        case 'deployment_update':
            updateDeploymentStatus(data.deployment_id, data.status, data.message);
            break;
        case 'log_update':
            updateDeploymentLogs(data.deployment_id, data.logs);
            break;
        case 'notification':
            showNotification(data.message, data.level);
            break;
        default:
            console.log('Unknown message type:', data.type);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.notification-container');
    if (container) {
        container.appendChild(alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Update submission status
function updateSubmissionStatus(submissionId, status, message) {
    const statusElement = document.getElementById(`submission-${submissionId}-status`);
    if (statusElement) {
        statusElement.className = `status-badge status-${status.toLowerCase()}`;
        statusElement.textContent = status;
    }

    const progressElement = document.getElementById(`submission-${submissionId}-progress`);
    if (progressElement) {
        progressElement.style.width = status === 'COMPLETED' ? '100%' :
                                   status === 'PROCESSING' ? '50%' : '0%';
    }
}

// Update deployment status
function updateDeploymentStatus(deploymentId, status, message) {
    const statusElement = document.getElementById(`deployment-${deploymentId}-status`);
    if (statusElement) {
        statusElement.className = `status-badge status-${status.toLowerCase()}`;
        statusElement.textContent = status;
    }

    // Update deployment logs if available
    if (message) {
        updateDeploymentLogs(deploymentId, [message]);
    }
}

// Update deployment logs
function updateDeploymentLogs(deploymentId, logs) {
    const logsContainer = document.getElementById(`deployment-${deploymentId}-logs`);
    if (logsContainer && logs) {
        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `<span class="timestamp">${new Date().toLocaleTimeString()}</span> ${log}`;
            logsContainer.appendChild(logEntry);
        });
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
}

// File upload handling
function setupFileUpload(uploadId, callback) {
    const uploadArea = document.getElementById(uploadId);
    if (!uploadArea) return;

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0], callback);
        }
    });

    const fileInput = uploadArea.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0], callback);
            }
        });
    }
}

// Handle file upload
function handleFileUpload(file, callback) {
    const validTypes = ['.cdc', '.sol'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!validTypes.includes(fileExtension)) {
        showNotification('Please upload a .cdc or .sol file', 'danger');
        return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        showNotification('File size must be less than 10MB', 'danger');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        callback(file.name, e.target.result);
    };
    reader.readAsText(file);
}

// Submit contract
async function submitContract(formData) {
    try {
        showNotification('Submitting contract...', 'info');

        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Submission failed');
        }

        const result = await response.json();
        currentSubmissionId = result.submission_id;

        showNotification('Contract submitted successfully!', 'success');

        // Redirect to deployment page if available
        if (result.redirect_url) {
            setTimeout(() => {
                window.location.href = result.redirect_url;
            }, 2000);
        }

        return result;
    } catch (error) {
        showNotification('Error submitting contract: ' + error.message, 'danger');
        throw error;
    }
}

// Deploy contract
async function deployContract(deploymentData) {
    try {
        showNotification('Starting deployment...', 'info');

        const response = await fetch('/api/deploy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(deploymentData)
        });

        if (!response.ok) {
            throw new Error('Deployment failed');
        }

        const result = await response.json();
        showNotification('Deployment started successfully!', 'success');

        return result;
    } catch (error) {
        showNotification('Error deploying contract: ' + error.message, 'danger');
        throw error;
    }
}

// Search documentation
async function searchDocumentation(query) {
    try {
        const response = await fetch(`/api/docs/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Search failed');
        }

        const results = await response.json();
        displaySearchResults(results);
        return results;
    } catch (error) {
        showNotification('Error searching documentation: ' + error.message, 'danger');
        throw error;
    }
}

// Display search results
function displaySearchResults(results) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;

    if (results.length === 0) {
        resultsContainer.innerHTML = '<p class="text-muted">No results found.</p>';
        return;
    }

    const resultsHtml = results.map(result => `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">${result.title}</h5>
                <h6 class="card-subtitle mb-2 text-muted">${result.content_type}</h6>
                <p class="card-text">${result.content.substring(0, 200)}...</p>
                <a href="#" class="btn btn-sm btn-outline-primary">View Full</a>
            </div>
        </div>
    `).join('');

    resultsContainer.innerHTML = resultsHtml;
}

// Format code display
function formatCode(code, language = 'cadence') {
    // Simple syntax highlighting (in production, use a library like Prism.js)
    const keywords = {
        cadence: ['pub', 'fun', 'let', 'var', 'const', 'if', 'else', 'for', 'while', 'return'],
        solidity: ['function', 'contract', 'address', 'uint', 'string', 'public', 'private', 'returns']
    };

    const langKeywords = keywords[language] || [];
    let formattedCode = code;

    langKeywords.forEach(keyword => {
        const regex = new RegExp(`\\b${keyword}\\b`, 'g');
        formattedCode = formattedCode.replace(regex, `<span class="keyword">${keyword}</span>`);
    });

    return `<pre><code class="language-${language}">${formattedCode}</code></pre>`;
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        showNotification('Failed to copy to clipboard', 'danger');
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize WebSocket
    initWebSocket();

    // Setup file upload areas
    setupFileUpload('file-upload-area', handleFileSelection);

    // Setup search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.trim();
            if (query.length > 2) {
                searchDocumentation(query);
            }
        }, 300));
    }

    // Setup copy buttons
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            copyToClipboard(textToCopy);
        });
    });
});

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.SmartContractLLM = {
    submitContract,
    deployContract,
    searchDocumentation,
    copyToClipboard,
    showNotification
};