package http

import (
	"net/http"

	"github.com/cosmetics/catalog-service/internal/catalog/domain"
	"github.com/cosmetics/catalog-service/internal/catalog/repository"
	"github.com/gin-gonic/gin"
)

type ShadeMatchRequest struct {
	TargetHexCode string  `json:"target_hex_code" binding:"required"`
	MaxDistance   float64 `json:"max_distance"`
}

type ShadeMatchResult struct {
	VariantID   string  `json:"variant_id"`
	ShadeName   string  `json:"shade_name"`
	HexCode     string  `json:"hex_code"`
	Undertone   string  `json:"undertone"`
	DeltaE      float64 `json:"delta_e"`
}

type ShadeHandler struct {
	cache *repository.InMemLRUCache
}

func NewShadeHandler(cache *repository.InMemLRUCache) *ShadeHandler {
	return &ShadeHandler{cache: cache}
}

func (h *ShadeHandler) MatchShade(c *gin.Context) {
	var req ShadeMatchRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	r, g, b, err := domain.HexToRGB(req.TargetHexCode)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid hex color format"})
		return
	}

	targetLab := domain.RGBToLAB(r, g, b)

	// Sample catalog palette
	palette := []ShadeMatchResult{
		{VariantID: "var_01", ShadeName: "Ivory Fair", HexCode: "#F5E3D0", Undertone: "COOL"},
		{VariantID: "var_02", ShadeName: "Golden Warm", HexCode: "#E2B88F", Undertone: "WARM"},
		{VariantID: "var_03", ShadeName: "Warm Olive", HexCode: "#C89562", Undertone: "OLIVE"},
		{VariantID: "var_04", ShadeName: "Deep Espresso", HexCode: "#4D3021", Undertone: "NEUTRAL"},
	}

	var bestMatch ShadeMatchResult
	minDelta := 999999.0

	for _, shade := range palette {
		sr, sg, sb, _ := domain.HexToRGB(shade.HexCode)
		slab := domain.RGBToLAB(sr, sg, sb)
		dist := domain.DeltaE76(targetLab, slab)
		shade.DeltaE = dist
		if dist < minDelta {
			minDelta = dist
			bestMatch = shade
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"matched_shade": bestMatch,
		"confidence":    fmtConfidence(bestMatch.DeltaE),
	})
}

func fmtConfidence(delta float64) string {
	if delta < 2.0 {
		return "EXACT_MATCH"
	} else if delta < 5.0 {
		return "HIGH_CONFIDENCE"
	}
	return "APPROXIMATE_MATCH"
}
