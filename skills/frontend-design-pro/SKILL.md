# Frontend Design Pro - Minimalism & Swiss Style

## Overview
This skill provides guidelines for creating clean, typography-focused interfaces following Swiss design principles. Used for the RumorLens rumor detection platform.

## Core Principles

### 1. Color Palette
```css
--color-bg: #faf9f7          /* Warm off-white background */
--color-text: #1a1a1a        /* Near-black text */
--color-accent: #e53935      /* Burnt red for emphasis/danger */
--color-success: #2e7d32     /* Deep green for verified/safe */
--color-warning: #f9a825     /* Amber for medium risk */
--color-muted: #666666       /* Muted gray for secondary text */
--color-border: #e5e5e5      /* Light border color */
```

### 2. Typography
- **Sans-serif**: Instrument Sans (weights: 400-700)
- **Serif**: Newsreader (for headlines, optical sizing 6-72)
- **Responsive scaling**: Use `clamp()` for fluid typography
  - H1: `clamp(2.5rem, 5vw, 4rem)`
  - Body: `1rem` with `1.6` line-height

### 3. Layout System
- 12-column CSS Grid
- Asymmetric distributions (7:4 or 8:4)
- Generous whitespace
- Max container width: 1400px
- Standard gap: 2rem

### 4. Animations
- Hover underline: width 0 to 100%, 0.3s ease
- Hover scale: scale(1.02), 0.4s cubic-bezier(0.16, 1, 0.3, 1)
- Fade-in-up: opacity 0->1, translateY 20px->0
- Stagger children: 50ms delay per item

## Forbidden Elements
- Gradient backgrounds
- Border-radius > 8px
- Heavy box shadows (blur > 20px)
- Decorative icons without function
- Default system fonts
- Emoji symbols
- Overly rounded elements
- AI-feeling decorative patterns

## Component Guidelines

### Cards
```css
.card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 2px;
  padding: 1.5rem;
  transition: box-shadow 0.3s ease;
}

.card:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}
```

### Buttons
```css
.button {
  border-radius: 2px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  transition: all 0.3s ease;
}

.button-primary {
  background: var(--color-text);
  color: var(--color-bg);
}

.button-primary:hover {
  background: var(--color-accent);
}
```

### Links
```css
.link {
  position: relative;
  color: var(--color-text);
}

.link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: currentColor;
  transition: width 0.3s ease;
}

.link:hover::after {
  width: 100%;
}
```

## Risk Level Visual Guide

### Low Risk (Verified)
- Color: #2e7d32 (green)
- Label: "LOW RISK" or "VERIFIED"

### Medium Risk
- Color: #f9a825 (amber)
- Label: "MEDIUM RISK"

### High Risk
- Color: #ef6c00 (orange)
- Label: "HIGH RISK"

### Critical Risk (Rumor)
- Color: #c62828 (red)
- Label: "CRITICAL" or "POTENTIAL RUMOR"

## Responsive Breakpoints
- Mobile: < 480px
- Tablet: 480px - 768px
- Desktop: 768px - 1200px
- Wide: > 1200px

## Accessibility
- Focus-visible states with 2px outline
- High contrast ratios (WCAG AA minimum)
- Semantic HTML structure
- Support for prefers-reduced-motion
