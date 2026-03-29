import ee

ee.Initialize(project='terrawatch-ai')

# -------------------------------
# ⚙️ CONFIG
# -------------------------------
MIN_AREA_HECTARES = 1  # Rule threshold

region = ee.Geometry.Rectangle([72.4, 23.0, 72.8, 23.3])

# -------------------------------
# 🌥️ Cloud Mask
# -------------------------------
def mask_s2_clouds(image):
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))

    return image.updateMask(mask).divide(10000)

# -------------------------------
# 🛰️ Image Loader
# -------------------------------
def get_image(start, end):
    return (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(mask_s2_clouds)
        .median()
    )

# -------------------------------
# 🌿 NDVI
# -------------------------------
def compute_ndvi(image):
    return image.normalizedDifference(['B8', 'B4']).rename('NDVI')

# -------------------------------
# 📡 Data
# -------------------------------
image_old = get_image("2022-01-01", "2022-02-01")
image_new = get_image("2023-01-01", "2023-02-01")

ndvi_old = compute_ndvi(image_old)
ndvi_new = compute_ndvi(image_new)

ndvi_change = ndvi_new.subtract(ndvi_old)

# -------------------------------
# 🎯 Detect Vegetation Loss
# -------------------------------
change_mask = ndvi_change.lt(-0.3).focal_max(radius=1)

polygons = change_mask.selfMask().reduceToVectors(
    geometry=region,
    scale=10,
    geometryType='polygon',
    eightConnected=True,
    labelProperty='change',
    maxPixels=1e9
)

# Add area
polygons = polygons.map(
    lambda f: f.set({'area_m2': f.geometry().area(1)})
)

# -------------------------------
# ⚖️ RULE ENGINE
# -------------------------------

def check_rules(feature):
    area_m2 = feature.get('area_m2')
    area_hectares = ee.Number(area_m2).divide(10000)

    violation = area_hectares.gt(MIN_AREA_HECTARES)

    return feature.set({
        'area_hectares': area_hectares,
        'violation': violation
    })

# Apply rules
polygons = polygons.map(check_rules)

# -------------------------------
# 📊 ANALYSIS
# -------------------------------
violations = polygons.filter(ee.Filter.eq('violation', True))
non_violations = polygons.filter(ee.Filter.eq('violation', False))

total = polygons.size().getInfo()
violated = violations.size().getInfo()

print("\n⚖️ ==== COMPLIANCE REPORT ====")
print(f"Total Regions: {total}")
print(f"Violations Detected: {violated}")

# Sample violations
sample = violations.limit(5).getInfo()

print("\n🚨 Sample Violations:")
for i, f in enumerate(sample['features']):
    area = f['properties']['area_hectares']
    print(f"Region {i+1}: {area:.2f} hectares → VIOLATION")

# -------------------------------
# 🌍 (Optional Visualization later)
# -------------------------------