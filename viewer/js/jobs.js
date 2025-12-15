/**
 * Service de gestion des jobs asynchrones
 * Permet de lancer des tâches longues et de suivre leur progression
 */

const JobService = {
    POLL_INTERVAL: 2000, // 2 secondes
    activePolls: new Map(),
    
    /**
     * Lance un job et retourne immédiatement le job_id
     */
    async startJob(endpoint, params = {}) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ ...params, async: true })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start job');
        }
        
        const data = await response.json();
        return data.job_id;
    },
    
    /**
     * Récupère le statut d'un job
     */
    async getJobStatus(jobId) {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`);
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Job not found - API may have restarted');
            }
            throw new Error('Failed to get job status');
        }
        return await response.json();
    },
    
    /**
     * Poll un job jusqu'à completion
     */
    pollJob(jobId, callbacks = {}) {
        const { onUpdate, onComplete, onError } = callbacks;
        
        const poll = async () => {
            try {
                const job = await this.getJobStatus(jobId);
                
                if (onUpdate) {
                    onUpdate(job);
                }
                
                if (job.status === 'completed') {
                    this.stopPolling(jobId);
                    if (onComplete) {
                        onComplete(job.result);
                    }
                } else if (job.status === 'failed') {
                    this.stopPolling(jobId);
                    if (onError) {
                        onError(job.error || 'Job failed');
                    }
                }
            } catch (e) {
                this.stopPolling(jobId);
                if (onError) {
                    onError(e.message);
                }
            }
        };
        
        // Premier appel immédiat
        poll();
        
        // Puis polling régulier
        const intervalId = setInterval(poll, this.POLL_INTERVAL);
        this.activePolls.set(jobId, intervalId);
        
        return jobId;
    },
    
    /**
     * Arrête le polling d'un job
     */
    stopPolling(jobId) {
        const intervalId = this.activePolls.get(jobId);
        if (intervalId) {
            clearInterval(intervalId);
            this.activePolls.delete(jobId);
        }
    },
    
    /**
     * Arrête tous les pollings actifs
     */
    stopAllPolling() {
        for (const [jobId, intervalId] of this.activePolls) {
            clearInterval(intervalId);
        }
        this.activePolls.clear();
    },
    
    /**
     * Liste tous les jobs (optionnellement pour un univers)
     */
    async listJobs(universe = null) {
        const url = universe 
            ? `${API_BASE}/jobs?universe=${encodeURIComponent(universe)}`
            : `${API_BASE}/jobs`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to list jobs');
        }
        return await response.json();
    }
};


/**
 * Helper pour lancer un job avec UI intégrée
 * @param {Object} options
 * @param {string} options.endpoint - Endpoint à appeler
 * @param {Object} options.params - Paramètres du job
 * @param {HTMLElement} options.statusElement - Element pour afficher le statut
 * @param {HTMLElement} options.buttonElement - Bouton à désactiver pendant le job
 * @param {Function} options.onComplete - Callback quand terminé
 * @param {string} options.successMessage - Message de succès
 */
async function runJobWithUI(options) {
    const { 
        endpoint, 
        params = {}, 
        statusElement, 
        buttonElement,
        onComplete,
        successMessage = 'Completed!'
    } = options;
    
    const originalButtonText = buttonElement?.textContent;
    
    try {
        // Désactiver le bouton
        if (buttonElement) {
            buttonElement.disabled = true;
            buttonElement.textContent = '⏳ Starting...';
        }
        if (statusElement) {
            statusElement.textContent = '⏳ Démarrage...';
            statusElement.className = 'job-status pending';
        }
        
        // Lancer le job
        const jobId = await JobService.startJob(endpoint, params);
        
        // Polling
        JobService.pollJob(jobId, {
            onUpdate: (job) => {
                if (buttonElement) {
                    buttonElement.textContent = `⏳ ${job.progress || job.status}...`;
                }
                if (statusElement) {
                    statusElement.textContent = `⏳ ${job.progress || job.status}...`;
                    statusElement.className = 'job-status running';
                }
            },
            onComplete: (result) => {
                if (buttonElement) {
                    buttonElement.disabled = false;
                    buttonElement.textContent = originalButtonText;
                }
                if (statusElement) {
                    statusElement.textContent = `✅ ${successMessage}`;
                    statusElement.className = 'job-status completed';
                }
                showToast(successMessage, 'success');
                if (onComplete) {
                    onComplete(result);
                }
            },
            onError: (error) => {
                if (buttonElement) {
                    buttonElement.disabled = false;
                    buttonElement.textContent = originalButtonText;
                }
                if (statusElement) {
                    statusElement.textContent = `❌ ${error}`;
                    statusElement.className = 'job-status failed';
                }
                showToast(`Error: ${error}`, 'error');
            }
        });
        
        return jobId;
        
    } catch (e) {
        // Erreur au démarrage
        if (buttonElement) {
            buttonElement.disabled = false;
            buttonElement.textContent = originalButtonText;
        }
        if (statusElement) {
            statusElement.textContent = `❌ ${e.message}`;
            statusElement.className = 'job-status failed';
        }
        showToast(`Failed to start: ${e.message}`, 'error');
        throw e;
    }
}


/**
 * Affiche la liste des jobs actifs pour l'univers courant
 */
async function showActiveJobs() {
    if (!currentUniverse) return;
    
    try {
        const { jobs, active } = await JobService.listJobs(currentUniverse);
        
        if (jobs.length === 0) {
            console.log('No jobs for this universe');
            return;
        }
        
        console.log(`Jobs for ${currentUniverse}:`, jobs);
        console.log(`Active jobs: ${active}`);
        
        // On pourrait afficher un panneau avec les jobs ici
        
    } catch (e) {
        console.error('Failed to list jobs:', e);
    }
}


// Cleanup quand on quitte la page
window.addEventListener('beforeunload', () => {
    JobService.stopAllPolling();
});

console.log('✅ Job service loaded');
