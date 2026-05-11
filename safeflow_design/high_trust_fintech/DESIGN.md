---
name: High-Trust FinTech
colors:
  surface: '#fcf8fb'
  surface-dim: '#dcd9db'
  surface-bright: '#fcf8fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f5'
  surface-container: '#f0edef'
  surface-container-high: '#eae7ea'
  surface-container-highest: '#e5e1e4'
  on-surface: '#1b1b1d'
  on-surface-variant: '#46464d'
  inverse-surface: '#313032'
  inverse-on-surface: '#f3f0f2'
  outline: '#77767e'
  outline-variant: '#c7c5ce'
  surface-tint: '#585d77'
  primary: '#03071d'
  on-primary: '#ffffff'
  primary-container: '#1a1f36'
  on-primary-container: '#8286a2'
  inverse-primary: '#c1c5e3'
  secondary: '#5d5f5f'
  on-secondary: '#ffffff'
  secondary-container: '#dfe0e0'
  on-secondary-container: '#616363'
  tertiary: '#020919'
  on-tertiary: '#ffffff'
  tertiary-container: '#172131'
  on-tertiary-container: '#7e889c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dde1ff'
  primary-fixed-dim: '#c1c5e3'
  on-primary-fixed: '#151a31'
  on-primary-fixed-variant: '#41455f'
  secondary-fixed: '#e2e2e2'
  secondary-fixed-dim: '#c6c6c7'
  on-secondary-fixed: '#1a1c1c'
  on-secondary-fixed-variant: '#454747'
  tertiary-fixed: '#d9e3f9'
  tertiary-fixed-dim: '#bdc7dc'
  on-tertiary-fixed: '#121c2b'
  on-tertiary-fixed-variant: '#3d4759'
  background: '#fcf8fb'
  on-background: '#1b1b1d'
  surface-variant: '#e5e1e4'
typography:
  display:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-margin: 20px
  gutter: 16px
---

## Brand & Style

The design system is rooted in the "Modern Corporate" aesthetic, prioritizing clarity, efficiency, and institutional reliability. It targets a sophisticated user base that values speed and precision in financial management. 

The visual narrative focuses on **Minimalism** to reduce cognitive load during complex financial tasks. By utilizing generous whitespace and a restricted color palette, the system directs attention toward critical transaction data. The emotional response is one of calm control—achieved through a balance of "High-Trust" deep indigos and a "Crisp" structural framework that feels both premium and approachable.

## Colors

This design system utilizes a high-contrast foundation. **Deep Indigo** (#1A1F36) serves as the primary anchor for brand elements, primary actions, and heavy headers, ensuring a professional and authoritative tone. **Crisp White** is the primary canvas, used to maintain a sense of openness and cleanliness.

The semantic palette is strictly reserved for transaction states and system feedback:
- **Emerald Green**: Indicates successful, cleared, or approved transactions.
- **Amber/Gold**: Indicates pending, flagged, or warning states.
- **Crimson Red**: Indicates declined, failed, or urgent errors.

Neutral greys are used exclusively for secondary information and structural borders to prevent visual competition with the primary brand colors.

## Typography

The design system employs **Inter** for its exceptional readability and systematic feel. The type hierarchy is designed to highlight monetary values and transaction titles.

- **Display & Headlines**: Use tight letter-spacing and bold weights to establish a strong visual anchor for balances.
- **Body Text**: Uses a standard weight with comfortable line heights to ensure readability of transaction details and terms.
- **Labels**: Slightly increased letter-spacing in uppercase or semi-bold variants is used for secondary metadata (e.g., timestamps, merchant categories).

## Layout & Spacing

The design system follows a **8px grid system** for consistent vertical rhythm. The layout model is a **fluid grid** with fixed side margins (20px) to ensure content remains centered and readable across various mobile screen widths.

A philosophy of "generous whitespace" is applied between functional groups (e.g., between the account balance and the transaction list) to prevent the UI from feeling cluttered. Spacing should be used to group related items (8px) and separate distinct sections (24px-32px).

## Elevation & Depth

Hierarchy is established using **Tonal Layers** and **Ambient Shadows**. The background layer is a soft neutral grey (#F7F9FC), while active cards and surfaces are pure white (#FFFFFF).

To create a sense of tactile depth without being skeuomorphic, the system uses "Extra-diffused" shadows. Shadows should have a large blur radius (20px+), low opacity (around 4-6%), and a slight vertical offset to suggest the element is hovering just above the surface. 

**Thin Dividers** (1px, #E6E8EB) are used within cards to separate list items, maintaining a clean structure without adding visual weight.

## Shapes

The design system features a "Large Rounded" shape language to soften the professional aesthetic and make the app feel modern and friendly. 

- **Primary Containers**: 16px (1rem) for transaction cards and main UI blocks.
- **Interactive Elements**: 12px for input fields and smaller buttons.
- **Status Badges**: Fully pill-shaped (capsule) to distinguish them from interactive buttons and cards.

## Components

### Buttons
- **Primary**: Deep Indigo background with white text. High contrast, 16px corner radius, bold weight.
- **Secondary**: White background with a thin indigo border or a soft grey ghost button for less critical actions.

### Cards & Transactions
- **Transaction Cards**: White surface, 16px corner radius, subtle ambient shadow. 
- **Internal Layout**: Icon on the left (rounded 12px background), Merchant/Title and Category in the center, and Amount on the right. 
- **Dividers**: Used only between list items within a single card.

### Status Badges
- Small, pill-shaped indicators.
- Use a light tint of the semantic color for the background (10% opacity) and the full-strength semantic color for the text to ensure accessibility while maintaining the color-coding.

### Input Fields
- Subtle 1px border (#E6E8EB), 12px corner radius. Focus state shifts the border to Primary Indigo or adds a soft indigo glow.

### Progress & Data
- Thin, rounded progress bars for "Budgeting" or "Savings Goals" features, using the Emerald Green to indicate positive progress.