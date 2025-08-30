// static/js/api.js - Improved version
const API_BASE_URL = '/api';

class ApiService {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        };

        const config = { ...defaultOptions, ...options };
        
        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Auth methods
    static async login(email, password) {
        return this.request('/login', {
            method: 'POST',
            body: { email, password }
        });
    }

    static async logout() {
        return this.request('/logout', {
            method: 'POST'
        });
    }

    static async checkAuth() {
        return this.request('/check-auth');
    }

    static async getJobOffers() {
        return this.request('/job-offers');
    }

    static async createJobOffer(offer) {
        return this.request('/job-offers', {
            method: 'POST',
            body: offer
        });
    }

static async updateJobOffer(id, offer) {
    return this.request(`/job-offers/${id}`, {
        method: 'PUT',
        body: offer
    });
}

static async deleteJobOffer(id) {
    return this.request(`/job-offers/${id}`, {
        method: 'DELETE'
    });
}   

    // Applications methods
    static async getApplications() {
        return this.request('/applications');
    }

    static async createApplication(application) {
        return this.request('/applications', {
            method: 'POST',
            body: application
        });
    }

    static async updateApplication(id, updates) {
    return this.request(`/applications/${int(id)}`, {
        method: 'PUT',
        body: updates
    });
}

    // In api.js - Update the deleteApplication method
    static async deleteApplication(identifier) {
        return this.request(`/applications/${encodeURIComponent(identifier)}`, {
            method: 'DELETE'
        });
    }

    // Dashboard methods
    static async getDashboardStats() {
        return this.request('/dashboard-stats');
        
    }
    // In api.js - Change from reset_password to reset-password
   // In api.js - Add these methods for candidates
static async getCandidates() {
    return this.request('/candidates');
}

static async createCandidate(candidate) {
    return this.request('/candidates', {
        method: 'POST',
        body: candidate
    });
}

static async updateCandidate(id, updates) {
    return this.request(`/candidates/${id}`, {
        method: 'PUT',
        body: updates
    });
}

static async deleteCandidate(id) {
    return this.request(`/candidates/${id}`, {
        method: 'DELETE'
    });
}   
// Add to api.js
static async getInterviews() {
    return this.request('/interviews');
}

static async createInterview(interview) {
    return this.request('/interviews', {
        method: 'POST',
        body: interview
    });
}

static async updateInterview(id, updates) {
    return this.request(`/interviews/${id}`, {
        method: 'PUT',
        body: updates
    });
}

static async deleteInterview(id) {
    return this.request(`/interviews/${id}`, {
        method: 'DELETE'
    });
}

}