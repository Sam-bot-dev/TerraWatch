# 🌍 TerraWatch AI

> Satellite Imagery Change Detection for Urban Expansion Monitoring & Land Use Compliance

---

## 🚀 Overview

**TerraWatch AI** is an intelligent geospatial monitoring system that leverages satellite imagery and AI to detect, classify, and analyze land-use changes over time.

With rapid urbanization, manual monitoring is no longer scalable. TerraWatch automates this process using:

* 🛰️ Satellite imagery (Sentinel-2, Landsat)
* 🤖 Deep learning-based change detection
* 📊 Spectral analysis (NDVI, NDBI, MNDWI)
* ⚖️ Compliance rule engine
* 🗺️ Interactive visualization dashboard

---

## 🎯 Problem Statement

Urban growth is happening faster than authorities can monitor. This leads to:

* Unauthorized construction
* Encroachment on protected areas
* Loss of green cover
* Violation of zoning laws

Manual satellite image analysis is:

* ❌ Slow
* ❌ Expensive
* ❌ Not scalable

---

## 💡 Solution

TerraWatch AI provides:

✅ Automated satellite image processing pipeline
✅ AI-based change detection (pixel + semantic level)
✅ Spectral index validation (NDVI, NDBI, MNDWI)
✅ Rule-based compliance violation detection
✅ Interactive map with time-based visualization
✅ Automated reports with insights and alerts

---

## 🧠 Core Features

### 1. 📡 Satellite Data Pipeline

* Download Sentinel-2 / Landsat imagery
* Cloud masking & atmospheric correction
* Multi-temporal alignment
* Composite generation

### 2. 🔍 Change Detection

* Binary change mask
* Change classification:

  * Vegetation loss 🌱
  * New construction 🏗️
  * Water changes 💧
  * Road expansion 🛣️
* Confidence scoring

### 3. 🌿 Spectral Analysis

* NDVI → Vegetation health
* NDBI → Built-up areas
* MNDWI → Water bodies

### 4. ⚖️ Compliance Engine

Configurable rules like:

* No construction near water bodies
* Maintain green cover threshold
* Zone-based restrictions

### 5. 📊 Reporting & Visualization

* Before/After comparison
* Area change (hectares)
* Violation alerts
* Interactive map with time slider

---

## 🏗️ Project Architecture

```
TerraWatch-AI/
│
├── data/                        # Raw & processed satellite data
│   ├── raw/
│   ├── processed/
│   └── outputs/
│
├── notebooks/                  # Experiments & analysis
│   ├── ndvi_analysis.ipynb
│   └── change_detection.ipynb
│
├── src/
│   ├── pipeline/               # Data ingestion & preprocessing
│   │   ├── downloader.py
│   │   ├── cloud_mask.py
│   │   ├── preprocessing.py
│   │   └── alignment.py
│   │
│   ├── indices/                # Spectral indices
│   │   ├── ndvi.py
│   │   ├── ndbi.py
│   │   └── mndwi.py
│   │
│   ├── models/                 # AI models
│   │   ├── siamese_unet.py
│   │   ├── changeformer.py
│   │   └── inference.py
│   │
│   ├── rules/                  # Compliance engine
│   │   ├── rules_engine.py
│   │   └── rules_config.json
│   │
│   ├── visualization/          # Map + outputs
│   │   ├── map.py
│   │   └── overlay.py
│   │
│   └── utils/
│       ├── geo_utils.py
│       └── io_utils.py
│
├── web/                        # Frontend (Leaflet / Mapbox)
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── reports/                    # Generated reports
│   ├── report_generator.py
│   └── templates/
│
├── tests/                      # Unit tests
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Tech Stack

### Backend

* Python
* Rasterio / GDAL
* NumPy, OpenCV
* PyTorch / TensorFlow

### Geospatial

* Google Earth Engine (optional)
* PostGIS

### Frontend

* Leaflet.js / Mapbox GL

### Storage

* Local / AWS S3

---

## 🧪 MVP Roadmap

### Phase 1 (Current Focus)

* [ ] Satellite image download
* [ ] NDVI calculation
* [ ] Basic change detection
* [ ] Visualization (static)

### Phase 2

* [ ] Deep learning model
* [ ] Multi-class change detection

### Phase 3

* [ ] Rule engine
* [ ] Web dashboard

### Phase 4

* [ ] Full automation + reports

---

## 🚀 Getting Started

### 1. Clone Repo

```
git clone https://github.com/yourusername/TerraWatch-AI.git
cd TerraWatch-AI
```

### 2. Setup Environment

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run First Script

```
python src/pipeline/downloader.py
```

---

## 📊 Evaluation Metrics

* Change Detection F1-score
* Classification Accuracy
* Rule Violation Precision
* Processing Speed (images/hour)

---

## 🌟 Future Scope

* Real-time monitoring
* Government integration APIs
* Mobile alerts for violations
* AI-driven urban planning insights

---

## 🤝 Contribution

Contributions are welcome! Open issues or submit PRs.

---

## 📜 License

MIT License

---

## 🔥 Vision

> TerraWatch aims to become the "AI Guardian of Urban Growth" — enabling smarter, compliant, and sustainable cities.
