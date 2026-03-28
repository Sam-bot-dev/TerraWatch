import ee
import geemap

# Initialize
ee.Initialize(project='terrawatch-ai')

# Define region (Ahmedabad)
region = ee.Geometry.Rectangle([72.4, 23.0, 72.8, 23.3])

# Function to mask clouds
def mask_s2_clouds(image):
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))

    return image.updateMask(mask).divide(10000)

# Load Sentinel-2 collection
def get_image(start, end):
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(mask_s2_clouds)
    )
    return collection.median()

# Two time periods
image1 = get_image("2022-01-01", "2022-02-01")
image2 = get_image("2023-01-01", "2023-02-01")

# NDVI function
def compute_ndvi(image):
    return image.normalizedDifference(['B8', 'B4']).rename('NDVI')

ndvi1 = compute_ndvi(image1)
ndvi2 = compute_ndvi(image2)

# Visualization
Map = geemap.Map(center=[23.02, 72.57], zoom=10)

ndvi_params = {
    'min': -1,
    'max': 1,
    'palette': ['blue', 'white', 'green']
}

Map.addLayer(ndvi1, ndvi_params, "NDVI 2022")
Map.addLayer(ndvi2, ndvi_params, "NDVI 2023")

Map.save("ndvi_map.html")
