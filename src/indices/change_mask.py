import ee
import geemap

ee.Initialize(project='terrawatch-ai')

region = ee.Geometry.Rectangle([72.4, 23.0, 72.8, 23.3])

def mask_s2_clouds(image):
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))

    return image.updateMask(mask).divide(10000)

def get_image(start, end):
    return (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(mask_s2_clouds)
        .median()
    )

def compute_ndvi(image):
    return image.normalizedDifference(['B8', 'B4']).rename('NDVI')

# Images
image_old = get_image("2022-01-01", "2022-02-01")
image_new = get_image("2023-01-01", "2023-02-01")

ndvi_old = compute_ndvi(image_old)
ndvi_new = compute_ndvi(image_new)

ndvi_change = ndvi_new.subtract(ndvi_old)

threshold = 0.2
change_mask = ndvi_change.abs().gt(threshold)

# -------------------------------
# 🔥 TERMINAL OUTPUT SECTION
# -------------------------------

print("\n📊 ==== NDVI ANALYSIS ====")

stats_old = ndvi_old.reduceRegion(
    reducer=ee.Reducer.minMax(),
    geometry=region,
    scale=10,
    maxPixels=1e9
).getInfo()

stats_new = ndvi_new.reduceRegion(
    reducer=ee.Reducer.minMax(),
    geometry=region,
    scale=10,
    maxPixels=1e9
).getInfo()

print(f"NDVI OLD → Min: {stats_old['NDVI_min']:.3f}, Max: {stats_old['NDVI_max']:.3f}")
print(f"NDVI NEW → Min: {stats_new['NDVI_min']:.3f}, Max: {stats_new['NDVI_max']:.3f}")

# Change stats
change_stats = ndvi_change.reduceRegion(
    reducer=ee.Reducer.minMax(),
    geometry=region,
    scale=10,
    maxPixels=1e9
).getInfo()

print("\n📉 ==== CHANGE ANALYSIS ====")
print(f"NDVI Change → Min: {change_stats['NDVI_min']:.3f}, Max: {change_stats['NDVI_max']:.3f}")

# Count changed pixels
pixel_area = ee.Image.pixelArea()

changed_area = change_mask.multiply(pixel_area).reduceRegion(
    reducer=ee.Reducer.sum(),
    geometry=region,
    scale=10,
    maxPixels=1e9
).getInfo()

total_area = pixel_area.reduceRegion(
    reducer=ee.Reducer.sum(),
    geometry=region,
    scale=10,
    maxPixels=1e9
).getInfo()

changed_m2 = list(changed_area.values())[0]
total_m2 = list(total_area.values())[0]

changed_hectares = changed_m2 / 10000
percentage = (changed_m2 / total_m2) * 100

print("\n📍 ==== DETECTION RESULT ====")
print(f"Changed Area: {changed_hectares:.2f} hectares")
print(f"Percentage Change: {percentage:.2f}%")

# -------------------------------
# MAP
# -------------------------------

Map = geemap.Map(center=[23.02, 72.57], zoom=10)

Map.addLayer(change_mask.updateMask(change_mask),
             {'palette': ['yellow']},
             "Detected Change")

Map.save("change_mask.html")