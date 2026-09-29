/**
 * public/js/api.js — Digital Savings Account Opening Platform Client API Client
 */

const API_BASE = ""; // Relative to host

const BankingAPI = {
    // ------------------------------------------------------------------------
    // Session State Management
    // ------------------------------------------------------------------------
    getSession: () => {
        try {
            return JSON.parse(sessionStorage.getItem("banking_session") || "{}");
        } catch (e) {
            return {};
        }
    },

    saveSession: (data) => {
        const current = BankingAPI.getSession();
        const merged = { ...current, ...data };
        sessionStorage.setItem("banking_session", JSON.stringify(merged));
        return merged;
    },

    clearSession: () => {
        sessionStorage.removeItem("banking_session");
    },

    // ------------------------------------------------------------------------
    // API Fetch Wrapper
    // ------------------------------------------------------------------------
    request: async (endpoint, method = "GET", body = null) => {
        const headers = {
            "Content-Type": "application/json",
            "Idempotency-Key": "idemp_" + Math.random().toString(36).substring(2, 15)
        };

        const config = {
            method,
            headers,
        };

        if (body && method !== "GET") {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);
            const data = await response.json();

            if (!response.ok) {
                console.error("API Error Response:", data);
                throw new Error(data.detail || data.title || "An unexpected API error occurred.");
            }
            return data;
        } catch (error) {
            console.error(`Fetch failed on ${endpoint}:`, error);
            throw error;
        }
    },

    // ------------------------------------------------------------------------
    // REST API Endpoint Methods
    // ------------------------------------------------------------------------
    healthCheck: async () => {
        return await BankingAPI.request("/health", "GET");
    },

    createSession: async (payload) => {
        const data = await BankingAPI.request("/api/v1/applications/session", "POST", payload);
        BankingAPI.saveSession(data);
        return data;
    },

    scanOCR: async (payload) => {
        const data = await BankingAPI.request("/api/v1/kyc/ocr-scan", "POST", payload);
        BankingAPI.saveSession({ kyc_ocr: data });
        return data;
    },

    verifyPersonalInfo: async (payload) => {
        const data = await BankingAPI.request("/api/v1/kyc/verify-personal-info", "POST", payload);
        BankingAPI.saveSession({ personal_verified: true, applicant_info: payload });
        return data;
    },

    verifyBiometrics: async (payload) => {
        const data = await BankingAPI.request("/api/v1/kyc/biometrics", "POST", payload);
        BankingAPI.saveSession({ biometrics: data });
        return data;
    },

    screenAML: async (payload) => {
        const data = await BankingAPI.request("/api/v1/compliance/aml-screen", "POST", payload);
        BankingAPI.saveSession({ aml_status: data });
        return data;
    },

    createAccount: async (payload) => {
        const data = await BankingAPI.request("/api/v1/accounts/create", "POST", payload);
        BankingAPI.saveSession({ account: data });
        return data;
    },

    issueCard: async (payload) => {
        const data = await BankingAPI.request("/api/v1/cards/issue", "POST", payload);
        BankingAPI.saveSession({ virtual_card: data });
        return data;
    },

    pushTokenize: async (payload) => {
        const data = await BankingAPI.request("/api/v1/cards/push-tokenize", "POST", payload);
        BankingAPI.saveSession({ wallet_token: data });
        return data;
    },

    getApplicationDetails: async (applicationId) => {
        return await BankingAPI.request(`/api/v1/applications/${applicationId}`, "GET");
    },

    getOnboardingStatus: async (sessionId) => {
        return await BankingAPI.request(`/api/v1/onboarding/status/${sessionId}`, "GET");
    },

    getAuditLedger: async () => {
        return await BankingAPI.request("/api/v1/audit/ledger", "GET");
    }
};

// Export to window for global browser usage
if (typeof window !== "undefined") {
    window.BankingAPI = BankingAPI;
}
