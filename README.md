# Data Analysis Project

**Group 10 — University of Basel**  
**Course:** Databases (CS246)  
**Semester:** Autumn 2025

**Authors:**
- Dario Manser
- Marvin George
- Nillan Sivarasa

---

## Project Overview

Choosing between public transport and a personal vehicle for daily commuting is often a matter of preference rather than data-driven reasoning.  
This project explores whether it’s possible to make that decision based on objective data, focusing on the reliability of each transport mode under suboptimal weather conditions.

---

## Datasets

The project uses multiple predefined and external datasets to analyze correlations between weather, traffic and
train delays.

### 1. Weather
- **Source:** 08-Weather-Swiss dataset
- **Size:** 50 MB
- **Format:** CSV
- **Content:** Temperature (`tre200d0`), precipitation (`rre150d0`), radiation (`gre000d0`), snow height (`hto000d0`), pressure (`prestad0`)
- **Temporal resolution:** Daily
- **Spatial resolution:** Station-based (Switzerland)

### 2. SBB Delays
- **Source:** 09-SBB-Ist-Daten dataset
- **Size:** 69 MB
- **Format:** CSV
- **Content:** Train ID, planned and actual times, line number, station ID
- **Temporal resolution:** Minute-level
- **Spatial resolution:** SBB station-level

### 3. UTD19
- **Source:** [ETH Zurich – UTD19](https://utd19.ethz.ch)
- **Size:** 7 GB
- **Format:** CSV
- **Temporal resolution:** Minute-level
- **Spatial resolution:** High-resolution grid (major Swiss cities like Zurich, Basel)

### 4. SBB Station Users (Daily Trend)
- **Source:** [Opendata Switzerland](https://opendata.swiss/de/dataset/anzahl-sbb-bahnhofbenutzer-tagesverlauf/resource/80d6ef26-1e63-46b0-832e-eac3dfa47718)
- **Size:** 69 KB
- **Format:** CSV / JSON
- **Temporal resolution:** Hourly
- **Spatial resolution:** Station-level

### 5. Public Holidays
- **Source:** [City of Zurich – Holidays Dataset](https://data.stadt-zuerich.ch/dataset/ssd_schulferien/resource/aad477f6-db39-4d1b-92d8-0885f2d363d1)
- **Size:** 27 KB
- **Format:** CSV
- **Temporal resolution:** Daily
- **Spatial resolution:** Zurich

---

## Analysis Goals

The analysis focuses on quantifying reliability for both trains and road traffic in adverse weather conditions.

1. **Weather classification:** Identify days with challenging weather (rain, snow, extreme cold/heat).
2. **Data matching:** Correlate weather data with:
  - Train delays (SBB data)
  - Road traffic density (UTD19 dataset)
  - Station occupancy (SBB station users dataset)
3. **Normalization:**
  - Account for weekends and public holidays using the holidays dataset.
  - Adjust commuter numbers accordingly.

### Reliability Metrics

- **Train system:**
  Correlation between bad weather and the number/severity of delays.

- **Road system:**
  Since direct delay data is unavailable, reliability is inferred indirectly:
  - Assumption 1: People generally stick to their usual transport mode.
  - Assumption 2: Daily commuting volume is roughly constant.
  → Therefore, a noticeable drop in vehicle counts under poor weather conditions implies reduced reliability.

**Goal:** Provide a data-driven statement comparing the **reliability of the Swiss train system** vs. **the road network** during suboptimal weather.

---

## Tools & Technologies

| Tool / Library | Purpose |
|----------------|----------|
| **Python** | Data cleaning, preprocessing, and PostgreSQL interaction |
| **PostgreSQL** | Database management and querying |

---
