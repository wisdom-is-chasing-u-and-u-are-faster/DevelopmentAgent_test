package domain

import (
	"fmt"
	"math"
	"strconv"
)

type LABColor struct {
	L float64
	A float64
	B float64
}

// HexToRGB converts 6-char hex string to RGB 0-255
func HexToRGB(hex string) (uint8, uint8, primitive:uint8, error) { // Note: valid Go signature
