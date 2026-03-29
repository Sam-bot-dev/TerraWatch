import ee

ee.Initialize(project='terrawatch-ai')

# -------------------------------
# ⚙️ CONFIG
# -------------------------------
BUFFER_DISTANCE = 500  # meters

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
# 🛰️ Load Image
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
# 🌊 MNDWI (Water Detection)
# -------------------------------
def compute_mndwi(image):
    return image.normalizedDifference(['B3', 'B11']).rename('MNDWI')

# -------------------------------
# 📡 Data
# -------------------------------
image_old = get_image("2022-01-01", "2022-02-01")
image_new = get_image("2023-01-01", "2023-02-01")

# NDVI change (for urbanization)
ndvi_change = compute_ndvi(image_new).subtract(compute_ndvi(image_old))

# Detect vegetation loss
change_mask = ndvi_change.lt(-0.3).focal_max(radius=1)

change_polygons = change_mask.selfMask().reduceToVectors(
    geometry=region,
    scale=10,
    geometryType='polygon',
    eightConnected=True,
    maxPixels=1e9
)

# -------------------------------
# 🌊 WATER DETECTION
# -------------------------------
mndwi = compute_mndwi(image_new)

water_mask = mndwi.gt(0.2)

water_polygons = water_mask.selfMask().reduceToVectors(
    geometry=region,
    scale=10,
    geometryType='polygon',
    maxPixels=1e9
)

# -------------------------------
# 🔵 BUFFER WATER (500m)
# -------------------------------
water_buffer = water_polygons.map(
    lambda f: f.buffer(BUFFER_DISTANCE)
)

# Merge all buffers into one geometry
water_buffer_union = water_buffer.geometry()

# -------------------------------
# ⚖️ CHECK VIOLATIONS
# -------------------------------
def check_water_violation(feature):
    intersects = feature.geometry().intersects(water_buffer_union, 1)

    return feature.set({
        'near_water_violation': intersects
    })

change_polygons = change_polygons.map(check_water_violation)

# -------------------------------
# 📊 ANALYSIS
# -------------------------------
violations = change_polygons.filter(
    ee.Filter.eq('near_water_violation', True)
)

total = change_polygons.size().getInfo()
violated = violations.size().getInfo()

print("\n🌊 ==== WATER PROTECTION REPORT ====")
print(f"Total Change Regions: {total}")
print(f"Violations Near Water: {violated}")

# Sample violations
sample = violations.limit(5).getInfo()

print("\n🚨 Sample Water Violations:")
for i, f in enumerate(sample['features']):
    print(f"Region {i+1}: Near water body → VIOLATION")