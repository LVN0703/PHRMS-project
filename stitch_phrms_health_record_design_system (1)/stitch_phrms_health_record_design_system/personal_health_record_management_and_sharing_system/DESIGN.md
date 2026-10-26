---
name: Personal Health Record Management and Sharing System
colors:
  surface: '#f7fafd'
  surface-dim: '#d7dade'
  surface-bright: '#f7fafd'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f4f8'
  surface-container: '#ebeef2'
  surface-container-high: '#e5e8ec'
  surface-container-highest: '#e0e3e7'
  on-surface: '#181c1f'
  on-surface-variant: '#3f484e'
  inverse-surface: '#2d3134'
  inverse-on-surface: '#eef1f5'
  outline: '#6f787f'
  outline-variant: '#bfc8cf'
  surface-tint: '#00658b'
  primary: '#006184'
  on-primary: '#ffffff'
  primary-container: '#007ba7'
  on-primary-container: '#f5faff'
  inverse-primary: '#7cd0ff'
  secondary: '#006a6a'
  on-secondary: '#ffffff'
  secondary-container: '#90efef'
  on-secondary-container: '#006e6e'
  tertiary: '#834d00'
  on-tertiary: '#ffffff'
  tertiary-container: '#a36410'
  on-tertiary-container: '#fff8f4'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c4e7ff'
  primary-fixed-dim: '#7cd0ff'
  on-primary-fixed: '#001e2c'
  on-primary-fixed-variant: '#004c69'
  secondary-fixed: '#93f2f2'
  secondary-fixed-dim: '#76d6d5'
  on-secondary-fixed: '#002020'
  on-secondary-fixed-variant: '#004f4f'
  tertiary-fixed: '#ffdcbc'
  tertiary-fixed-dim: '#ffb86c'
  on-tertiary-fixed: '#2c1600'
  on-tertiary-fixed-variant: '#683c00'
  background: '#f7fafd'
  on-background: '#181c1f'
  surface-variant: '#e0e3e7'
  health-green: '#4CAF50'
  aid-red: '#D62828'
  clean-white: '#FFFFFF'
  cool-gray: '#A9B0B3'
  app-bg: '#F4F7F8'
  text-primary: '#1E293B'
  text-secondary: '#5A6570'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  mono-data:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 24px
  margin: 32px
  space-xs: 4px
  space-sm: 8px
  space-md: 16px
  space-lg: 24px
  space-xl: 32px
---

# Design.md — Google Stitch UI/UX Specification & Typography Guide
**Application Name:** Personal Health Record Management and Sharing System (PHRMS)  
**Target Platform:** Desktop & Laptop Web Application (`1440px` – `1280px` primary viewport, responsive `12-column` grid)  
**Visual Theme:** Clean, Trustworthy Clinical SaaS Dashboard (Light Mode Only)  

## 1. Global Color Palette Tokens (Medical Logo Palette)
* **Primary Brand / Patient Accent (`Surgical Blue`):** `#007BA7`  
  * *Hover State:* `#005F82` | *Soft Tint / Active Row Highlight:* `#E6F4F9`
* **Secondary Brand / Reviewer & Doctor Accent (`Trust Teal`):** `#008080`  
  * *Soft Tint / Banner Fill:* `#E6F2F2`
* **Positive / Approved / Authorized (`Health Green`):** `#4CAF50`  
  * *Soft Badge Fill:* `#E8F5E9` | *Badge Text:* `#1B5E20`
* **Critical / Rejected / Revoke / Allergy Alert (`Aid Red`):** `#D62828`  
  * *Soft Alert Fill:* `#FDEAEA` | *Badge Text:* `#991B1B`
* **Primary Card & Sheet Surface (`Clean White`):** `#FFFFFF`
* **Neutral Structural / Pending / Borders (`Cool Gray`):** `#A9B0B3`  
  * *App Background Canvas:* `#F4F7F8` | *Card Border:* `1px solid #DCE1E5`  
  * *Primary Heading & Body Text:* `#1E293B` | *Secondary Text:* `#5A6570`

## 2. Typography & Component Style System
* **UI Font Stack:** `'Inter'`, `'Plus Jakarta Sans'`, or system sans-serif.
* **Monospace Font Stack:** `'JetBrains Mono'`, `monospace` (used for Timestamps, Record IDs, and Reference Codes).
* **Border Radius:**
  * Cards & Modals: `12px`
  * Buttons & Form Inputs: `8px`
  * Status Pills & Category Badges: `9999px` (Full pill)
* **Elevation / Shadows:**
  * Standard Card: `0 2px 8px rgba(30, 41, 59, 0.06)`
  * Floating Modal / Summary Sheet: `0 10px 25px rgba(30, 41, 59, 0.12)`
