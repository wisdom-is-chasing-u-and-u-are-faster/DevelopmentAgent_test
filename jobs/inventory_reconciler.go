package main

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/lib/pq"
	"github.com/redis/go-redis/v9"
)

type Reconciler struct {
	db    *sql.DB
	rdb   *redis.Client
	ctx   context.Context
}

func NewReconciler(dbConnStr, redisAddr string) (*Reconciler, error) {
	ctx := context.Background()
	db, err := sql.Open("postgres", dbConnStr)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to postgres: %w", err)
	}

	rdb := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})

	return &Reconciler{db: db, rdb: rdb, ctx: ctx}, nil
}

func (r *Reconciler) ReconcileVariant(variantID string) (int, int, error) {
	var ledgerSum int
	query := `SELECT COALESCE(SUM(quantity_delta), 0) FROM inventory_ledger WHERE variant_id = $1`
	err := r.db.QueryRowContext(r.ctx, query, variantID).Scan(&ledgerSum)
	if err != nil {
		return 0, 0, fmt.Errorf("failed to query ledger: %w", err)
	}

	redisKey := fmt.Sprintf("stock:available:%s", variantID)
	val, err := r.rdb.Get(r.ctx, redisKey).Int()
	if err != nil && err != redis.Nil {
		return ledgerSum, 0, fmt.Errorf("failed to query redis stock: %w", err)
	}

	drift := ledgerSum - val
	if drift != 0 {
		log.Printf("[ALERT] Inventory drift detected for variant %s: DB Ledger=%d, Redis=%d, Drift=%d",
			variantID, ledgerSum, val, drift)
	} else {
		log.Printf("[OK] Variant %s in sync. Balance: %d", variantID, ledgerSum)
	}

	return ledgerSum, val, nil
}

func main() {
	log.Println("Starting Hourly Inventory Reconciliation Worker...")
	dbUrl := os.Getenv("DATABASE_URL")
	if dbUrl == "" {
		dbUrl = "postgres://postgres:postgres@localhost:5432/cosmetics?sslmode=disable"
	}
	redisHost := os.Getenv("REDIS_HOST")
	if redisHost == "" {
		redisHost = "localhost:6379"
	}

	rec, err := NewReconciler(dbUrl, redisHost)
	if err != nil {
		log.Fatalf("Init error: %v", err)
	}
	defer rec.db.Close()
	defer rec.rdb.Close()

	log.Println("Reconciliation worker initialized successfully.")
}
