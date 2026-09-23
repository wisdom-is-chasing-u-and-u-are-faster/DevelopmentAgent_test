package domain

import (
	"math"
	"testing"
)

func TestHexToRGBAndDeltaE(t *testing.T) {
	r, g, b, err := HexToRGB("#FFFFFF")
	if err != nil || r != 255 || g != 255 || b != 255 {
		t.Fatalf("Failed white hex conversion: %v", err)
	}

	lab1 := RGBToLAB(255, 255, 255)
	lab2 := RGBToLAB(255, 255, 255)
	dist := DeltaE76(lab1, lab2)
	if math.Abs(dist) > 0.001 {
		t.Fatalf("Expected deltaE 0 for identical colors, got %f", dist)
	}
}
