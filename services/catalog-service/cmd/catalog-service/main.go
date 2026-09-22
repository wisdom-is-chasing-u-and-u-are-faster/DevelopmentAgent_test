package main

import (
	"log"
	"time"

	"github.com/cosmetics/catalog-service/internal/catalog/delivery/http"
	"github.com/cosmetics/catalog-service/internal/catalog/repository"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	cache := repository.NewInMemLRUCache(300 * time.Second)
	shadeHandler := http.NewShadeHandler(cache)

	v1 := r.Group("/v1/catalog")
	{
		v1.POST("/shades/match", shadeHandler.MatchShade)
		v1.GET("/products/:slug", func(c *gin.Context) {
			slug := c.Param("slug")
			c.JSON(200, gin.H{"slug": slug, "status": "AVAILABLE"})
		})
	}

	log.Println("Catalog & Shade Matcher service running on :8080")
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Server startup failed: %v", err)
	}
}
