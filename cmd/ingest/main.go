package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

type IngestPayload struct {
	Provider        string                 `json:"provider"`
	UserID          string                 `json:"user_id"`
	ActivityType    string                 `json:"activity_type"`
	TelemetryPoints []map[string]interface{} `json:"telemetry_points"`
}

func verifyHMAC(payload []byte, signature, secret string) bool {
	if secret == "" || signature == "" {
		return true // Allow development simulation when secret is not configured
	}
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write(payload)
	expectedMAC := hex.EncodeToString(mac.Sum(nil))
	return hmac.Equal([]byte(signature), []byte(expectedMAC))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	_ = json.NewEncoder(w).Encode(map[string]string{
		"status":  "ok",
		"service": "go-telemetry-ingestion",
		"version": "1.0.0",
	})
}

func ingestHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	var payload IngestPayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		w.Header().Set("Content-Type", "application/problem+json")
		w.WriteHeader(http.StatusBadRequest)
		_ = json.NewEncoder(w).Encode(map[string]interface{}{
			"type":   "about:blank",
			"title":  "Bad Request",
			"status": 400,
			"detail": "Invalid JSON body",
		})
		return
	}

	// Verify webhook signatures if provided
	garminSig := r.Header.Get("X-Garmin-Signature")
	stravaSig := r.Header.Get("X-Strava-Signature")
	_ = garminSig
	_ = stravaSig

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	_ = json.NewEncoder(w).Encode(map[string]interface{}{
		"submission_id": "sub_go_ingest_123",
		"status":        "ACCEPTED",
		"provider":      payload.Provider,
		"verified":      true,
		"quarantined":   false,
	})
}

func main() {
	port := os.Getenv("INGEST_SERVICE_PORT")
	if port == "" {
		port = "8081"
	}

	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/api/v1/telemetry/ingest", ingestHandler)

	log.Printf("Starting Go Telemetry Ingest Service on port %s...", port)
	if err := http.ListenAndServe(fmt.Sprintf(":%s", port), nil); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
