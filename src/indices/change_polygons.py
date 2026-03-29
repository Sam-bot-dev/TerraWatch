import ee
import geemap

# Initialize Earth Engine
ee.Initialize(project='terrawatch-ai')

# Region (Ahmedabad)
region = ee.Geometry.Rectangle([72.4, 23.0, 72.8, 23.3])

# -------------------------------
# 🌥️ Cloud Mask Function
# -------------------------------
def mask_s2_clouds(image):
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))

    return image.updateMask(mask).divide(10000)

# -------------------------------
# 🛰️ Get Sentinel Image
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
# 🌿 NDVI Calculation
# -------------------------------
def compute_ndvi(image):
    return image.normalizedDifference(['B8', 'B4']).rename('NDVI')

# -------------------------------
# 📡 Load Images
# -------------------------------
image_old = get_image("2022-01-01", "2022-02-01")
image_new = get_image("2023-01-01", "2023-02-01")

ndvi_old = compute_ndvi(image_old)
ndvi_new = compute_ndvi(image_new)

# -------------------------------
# 🔥 NDVI Change
# -------------------------------
ndvi_change = ndvi_new.subtract(ndvi_old)

# -------------------------------
# 🎯 Detect Vegetation Loss
# -------------------------------
# Strict threshold for better results
change_mask = ndvi_change.lt(-0.3)

# Smooth mask (reduce fragmentation)
change_mask = change_mask.focal_max(radius=1)

# -------------------------------
# 🔷 VECTORIZE (Raster → Polygons)
# -------------------------------
polygons = change_mask.selfMask().reduceToVectors(
    geometry=region,
    scale=10,
    geometryType='polygon',
    eightConnected=True,
    labelProperty='change',
    maxPixels=1e9
)

# -------------------------------
# 📏 ADD AREA + FILTER NOISE
# -------------------------------
polygons = polygons.map(
    lambda f: f.set({'area_m2': f.geometry().area(1)})
)

# Remove small regions (< 0.5 hectare)
polygons = polygons.filter(ee.Filter.gt('area_m2', 5000))

# -------------------------------
# 📊 TERMINAL ANALYSIS
# -------------------------------
print("\n📍 ==== CLEANED POLYGON ANALYSIS ====")

count = polygons.size().getInfo()
print(f"Total Significant Change Regions: {count}")

# Sample regions
features = polygons.limit(5).getInfo()

print("\n🔍 Sample Regions:")
for i, f in enumerate(features['features']):
    area = f['properties']['area_m2'] / 10000  # convert to hectares
    print(f"Region {i+1}: {area:.2f} hectares")

# -------------------------------
# 🌍 VISUALIZATION
# -------------------------------
Map = geemap.Map(center=[23.02, 72.57], zoom=10)

# Change mask
Map.addLayer(change_mask.updateMask(change_mask),
             {'palette': ['red']},
             "Vegetation Loss")

# Polygons
Map.addLayer(polygons, {}, "Change Polygons")

# Save map
Map.save("change_polygons.html")

print("\n🌍 Map saved as change_polygons.html")
print("👉 Open using: xdg-open change_polygons.html")