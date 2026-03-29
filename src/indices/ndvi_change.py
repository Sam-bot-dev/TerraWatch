import ee
import geemap

# Initialize
ee.Initialize(project='terrawatch-ai')

# Region (Ahmedabad)
region = ee.Geometry.Rectangle([72.4, 23.0, 72.8, 23.3])

# Cloud mask
def mask_s2_clouds(image):
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))

    return image.updateMask(mask).divide(10000)

# Get image
def get_image(start, end):
    return (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(mask_s2_clouds)
        .median()
    )

# NDVI
def compute_ndvi(image):
    return image.normalizedDifference(['B8', 'B4']).rename('NDVI')

# Time periods
image_old = get_image("2022-01-01", "2022-02-01")
image_new = get_image("2023-01-01", "2023-02-01")

ndvi_old = compute_ndvi(image_old)
ndvi_new = compute_ndvi(image_new)

# Change detection
ndvi_change = ndvi_new.subtract(ndvi_old)

# Visualization
Map = geemap.Map(center=[23.02, 72.57], zoom=10)

# NDVI change visualization
change_params = {
    'min': -0.5,
    'max': 0.5,
    'palette': ['red', 'white', 'green']
}

Map.addLayer(ndvi_change, change_params, "NDVI Change")

Map.save("ndvi_change.html")