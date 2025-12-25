# Geospatial preferences (13 items)
GEOSPATIAL_PREFS = [
    {
        "category": "geospatial",
        "prompt": "What coordinate reference systems should I use for defense applications?",
        "chosen": """**CRS recommendations for defense:**

| CRS | Use Case | Format |
|-----|----------|--------|
| WGS84 | Global reference, GPS | Lat/Lon |
| UTM | Local mapping, measurement | Easting/Northing |
| MGRS | Military grid reference | Alphanumeric |

**WGS84 (EPSG:4326):** Geodetic datum, global, GPS native. Use for storage/exchange.

**UTM:** Projected, metric, 60 zones. Use for measurement.
```python
def get_utm_zone(longitude):
    return int((longitude + 180) / 6) + 1

def utm_epsg(zone, northern=True):
    return 32600 + zone if northern else 32700 + zone
```

**MGRS:** NATO standard, hierarchical precision.
```python
import mgrs
m = mgrs.MGRS()
mgrs_coord = m.toMGRS(38.8977, -77.0365, MGRSPrecision=5)  # '18SUJ2339407396'
lat, lon = m.toLatLon('18SUJ2339407396')
```

**Vertical datums:**

| Datum | Use Case |
|-------|----------|
| WGS84 ellipsoid | GPS direct |
| EGM2008 | Current geoid standard |
| NAVD88 | US surveying |

**3DGS recommendation:** Store WGS84, transform to UTM for measurement, display MGRS for military.""",
        "rejected": "Use WGS84 for GPS coordinates, UTM for measurements, and MGRS for military grid references. Transform between them as needed."
    },
    {
        "category": "geospatial",
        "prompt": "How do I create orthomosaic outputs from 3DGS?",
        "chosen": """**Orthomosaic from 3DGS:**

**Method 1: Render from nadir**
```python
def generate_ortho_from_3dgs(gaussians, bounds, gsd=0.1):
    width = int((bounds.east - bounds.west) / gsd)
    height = int((bounds.north - bounds.south) / gsd)
    
    ortho_camera = OrthographicCamera(
        position=[bounds.center_x, bounds.center_y, bounds.max_z + 100],
        look_at=[bounds.center_x, bounds.center_y, bounds.center_z],
        width=width, height=height
    )
    return render_gaussians(gaussians, ortho_camera)

def save_geotiff(ortho_rgb, bounds, output_path, epsg=4326):
    import rasterio
    from rasterio.transform import from_bounds
    transform = from_bounds(bounds.west, bounds.south, bounds.east, bounds.north,
                           ortho_rgb.shape[1], ortho_rgb.shape[0])
    with rasterio.open(output_path, 'w', driver='GTiff', 
                       height=ortho_rgb.shape[0], width=ortho_rgb.shape[1],
                       count=3, dtype=ortho_rgb.dtype, crs=f'EPSG:{epsg}',
                       transform=transform, compress='LZW') as dst:
        for i in range(3):
            dst.write(ortho_rgb[:, :, i], i + 1)
```

**Method 2: Tiled for large areas** (iterate grid cells)

**Method 3: Web map tiles (XYZ/TMS)** for serving

**Quality validation:** Geometric accuracy vs GCPs, seam visibility, color consistency""",
        "rejected": "Render the 3DGS from directly above with an orthographic camera and save as GeoTIFF with proper coordinates."
    },
    {
        "category": "geospatial",
        "prompt": "How do I generate a DEM from 3DGS?",
        "chosen": """**DEM generation from 3DGS:**

**DEM types:** DSM (surface), DTM (bare earth), DHM (DSM-DTM)

**Method 1: Gaussian sampling**
```python
def gaussians_to_dsm(gaussians, bounds, resolution=1.0):
    width = int((bounds.east - bounds.west) / resolution)
    height = int((bounds.north - bounds.south) / resolution)
    dsm = np.full((height, width), np.nan)
    
    for i in range(height):
        for j in range(width):
            x = bounds.west + j * resolution
            y = bounds.north - i * resolution
            distances = np.sqrt((gaussians.means[:, 0] - x)**2 + 
                               (gaussians.means[:, 1] - y)**2)
            nearby = distances < gaussians.scales[:, :2].max(axis=1) * 2
            if nearby.any():
                weights = gaussians.opacities[nearby] * (1 / (distances[nearby] + 0.1))
                dsm[i, j] = np.average(gaussians.means[nearby][:, 2], weights=weights)
    return dsm
```

**Method 2: Depth rendering from nadir**

**Method 3: CSF filter for DTM extraction**

**Derived products:**

| Product | Calculation | Use |
|---------|-------------|-----|
| Slope | arctan(dZ/dXY) | Mobility |
| Aspect | Steepest descent | Solar analysis |
| Hillshade | Simulated lighting | Visualization |
| Contours | Iso-elevation | Mapping |""",
        "rejected": "Sample the height of Gaussians at regular grid points or render depth from above. Save as GeoTIFF with elevation values."
    },
    {
        "category": "geospatial",
        "prompt": "How do I perform line-of-sight analysis with 3DGS?",
        "chosen": """**Line-of-sight (LOS) analysis:**

**Use cases:** Visibility analysis, viewshed, sensor coverage, concealment

**Point-to-point LOS:**
```python
def compute_los(gaussians, observer, target, samples=100):
    direction = target - observer
    distance = np.linalg.norm(direction)
    direction = direction / distance
    
    for t in np.linspace(0, distance, samples)[1:-1]:
        point = observer + t * direction
        if point_in_gaussians(gaussians, point):
            return {'visible': False, 'obstruction_distance': t}
    return {'visible': True, 'distance': distance}
```

**Viewshed computation:**
```python
def compute_viewshed(gaussians, observer, bounds, resolution=1.0):
    viewshed = np.zeros((height, width), dtype=bool)
    observer_pos = np.array([*observer[:2], observer[2] + 1.8])
    
    for i, j in grid_positions:
        x, y = bounds_to_coords(i, j)
        z = get_terrain_height(gaussians, x, y)
        target = np.array([x, y, z + 1.0])
        viewshed[i, j] = compute_los(gaussians, observer_pos, target)['visible']
    return viewshed
```

**Output products:**
- Binary viewshed (visible/not)
- Visibility count (how many observers see each point)
- Dead space map (areas not visible from any position)""",
        "rejected": "Cast rays from observer to target points and check for Gaussian intersections. Repeat across a grid for viewshed analysis."
    },
    {
        "category": "geospatial",
        "prompt": "What is NITF format and do I need to support it?",
        "chosen": """**NITF = National Imagery Transmission Format** (DoD/IC standard)

**Structure:**
- File Header (classification, handling)
- Image Segment(s) (data, georef)
- Text Segment(s) (reports)
- Data Extension Segment(s) (TREs)

**Key TREs:** GEOLOB (location), RPC00B (sensor model), CSEXRA (exploitation)

**When to support:**

| Use Case | NITF Required? |
|----------|----------------|
| DoD/IC products | Yes |
| GEOINT integration | Yes |
| Commercial satellite | Often |
| Commercial apps | No (GeoTIFF) |

**Python handling:**
```python
from osgeo import gdal
ds = gdal.Open('image.ntf')
image = ds.ReadAsArray()
metadata = ds.GetMetadata('TRE')
rpc = ds.GetMetadata('RPC')
```

**Writing NITF:**
```python
driver = gdal.GetDriverByName('NITF')
ds = driver.Create(output_path, width, height, 3, gdal.GDT_Byte,
    options=['ICORDS=G', 'ICAT=VIS', f'FSCLAS={classification}', 'IREP=RGB'])
```

**Orb recommendation:** Support NITF export for DoD. Commercial/research: GeoTIFF (Cloud Optimized) is simpler.""",
        "rejected": "NITF is the military standard for imagery. Support it if you need to integrate with DoD systems, otherwise GeoTIFF works."
    },
    {
        "category": "geospatial",
        "prompt": "How do I integrate 3DGS with GIS software like QGIS or ArcGIS?",
        "chosen": """**GIS integration pathways:**

| System | Formats |
|--------|---------|
| QGIS | GeoTIFF, GPKG, LAZ |
| ArcGIS Pro | SLPK, GeoTIFF, LAS |
| Cesium | 3D Tiles, glTF |

**Export as point cloud:**
```python
import laspy

def export_gaussians_to_las(gaussians, output_path, epsg=32618):
    valid = gaussians.opacities > 0.3
    points = gaussians.means[valid]
    colors = (gaussians.colors[valid] * 255).astype(np.uint8)
    
    header = laspy.LasHeader(point_format=2, version="1.4")
    las = laspy.LasData(header)
    las.x, las.y, las.z = points[:, 0], points[:, 1], points[:, 2]
    las.red, las.green, las.blue = colors[:, 0]*256, colors[:, 1]*256, colors[:, 2]*256
    las.header.add_crs(epsg)
    las.write(output_path)
```

**Full GIS package:**
```python
def export_gis_package(gaussians, bounds, output_dir):
    save_cog(generate_ortho(gaussians, bounds), f'{output_dir}/ortho.tif')
    save_geotiff(gaussians_to_dsm(gaussians, bounds), f'{output_dir}/dsm.tif')
    generate_contours(dem, interval=1.0).to_file(f'{output_dir}/contours.gpkg')
    export_gaussians_to_las(gaussians, f'{output_dir}/pointcloud.laz')
```

**For Cesium:** Export as 3D Tiles for web visualization.""",
        "rejected": "Export as GeoTIFF for 2D layers, LAS for point clouds, or mesh formats for 3D. Each GIS system has preferred formats."
    },
    {
        "category": "geospatial",
        "prompt": "How do I validate the positional accuracy of a 3DGS reconstruction?",
        "chosen": """**Positional accuracy validation:**

**Metrics:**

| Metric | Definition |
|--------|------------|
| RMSE | √(Σ(error²)/n) |
| CE90 | 90th percentile horizontal |
| LE90 | 90th percentile vertical |
| NSSDA | 1.7308 × RMSE |

**Validation workflow:**
```python
class AccuracyValidator:
    def __init__(self, gcps):  # [{'survey': [x,y,z], 'model': [x,y,z]}]
        self.gcps = gcps
        
    def compute_statistics(self):
        errors = [{'horizontal': np.linalg.norm(gcp['model'][:2] - gcp['survey'][:2]),
                   'vertical': abs(gcp['model'][2] - gcp['survey'][2])} 
                  for gcp in self.gcps]
        horiz = np.array([e['horizontal'] for e in errors])
        vert = np.array([e['vertical'] for e in errors])
        return {
            'rmse_horizontal': np.sqrt(np.mean(horiz**2)),
            'rmse_vertical': np.sqrt(np.mean(vert**2)),
            'ce90': np.percentile(horiz, 90),
            'le90': np.percentile(vert, 90),
        }
```

**GCP requirements:** Min 20 for NSSDA, distributed, 3-5x better accuracy than target

**Accuracy targets:**

| Application | Horizontal | Vertical |
|-------------|------------|----------|
| Visualization | 5-10m | 5m |
| Mapping | 0.5-2m | 1m |
| Engineering | 0.05-0.1m | 0.1m |""",
        "rejected": "Compare model coordinates to surveyed ground control points. Calculate RMSE and check if it meets your accuracy requirements."
    },
    {
        "category": "geospatial",
        "prompt": "What is a sensor model and why is it important for georeferencing?",
        "chosen": """**Sensor model = Image ↔ Ground coordinate transformation**

**Types:**

| Type | Use Case |
|------|----------|
| RPC | Satellite imagery |
| Rigorous | High-precision |
| Frame | Central perspective (3DGS) |

**RPC (Rational Polynomial Coefficients):**
```
Column = Pc(φ,λ,h) / Qc(φ,λ,h)
Row = Pr(φ,λ,h) / Qr(φ,λ,h)
```
Where P, Q are 3rd-order polynomials (78 coefficients each).

**Frame camera model (for 3DGS):**
```python
class FrameCameraModel:
    def __init__(self, K, R, t, distortion=None):
        self.K = K  # 3x3 intrinsic
        self.R = R  # 3x3 rotation
        self.t = t  # 3x1 translation
    
    def world_to_image(self, world_point):
        cam_point = self.R @ world_point + self.t
        normalized = cam_point[:2] / cam_point[2]
        pixel = self.K @ np.array([*normalized, 1])
        return pixel[:2]
    
    def image_to_ray(self, pixel):
        normalized = np.linalg.inv(self.K) @ np.array([*pixel, 1])
        direction = self.R.T @ normalized
        origin = -self.R.T @ self.t
        return origin, direction / np.linalg.norm(direction)
```

**Why important:** COLMAP estimates frame model → georeferencing transforms to world CRS → accuracy depends on calibration quality.""",
        "rejected": "A sensor model converts between image coordinates and ground coordinates. RPCs are used for satellites, frame models for regular cameras."
    },
    {
        "category": "geospatial",
        "prompt": "How do I create a slope and aspect map from 3DGS terrain?",
        "chosen": """**Slope and aspect from 3DGS DEM:**

**Definitions:** Slope = rate of elevation change, Aspect = direction of steepest descent

**NumPy gradient:**
```python
def compute_slope_aspect(dem, resolution):
    dy, dx = np.gradient(dem, resolution)
    
    slope_radians = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_degrees = np.degrees(slope_radians)
    
    aspect_radians = np.arctan2(-dx, dy)
    aspect_degrees = np.degrees(aspect_radians)
    aspect_degrees = np.where(aspect_degrees < 0, aspect_degrees + 360, aspect_degrees)
    
    aspect_degrees[slope_degrees < 0.5] = -1  # Flat areas
    return slope_degrees, aspect_degrees
```

**Horn's method (better for noisy DEMs):**
```python
def horn_slope_aspect(dem, cell_size):
    dem_pad = np.pad(dem, 1, mode='edge')
    # Extract 8 neighbors
    dz_dx = ((z3 + 2*z6 + z9) - (z1 + 2*z4 + z7)) / (8 * cell_size)
    dz_dy = ((z1 + 2*z2 + z3) - (z7 + 2*z8 + z9)) / (8 * cell_size)
    # Compute slope and aspect...
```

**Using RichDEM:**
```python
import richdem as rd
dem = rd.LoadGDAL('dem.tif')
slope = rd.TerrainAttribute(dem, attrib='slope_degrees')
aspect = rd.TerrainAttribute(dem, attrib='aspect')
```

**Defense applications:** Slope for vehicle trafficability, aspect for solar/thermal planning.""",
        "rejected": "Calculate the gradient of the DEM in x and y directions, then compute slope as arctan of the magnitude and aspect as arctan2 of the components."
    },
    {
        "category": "geospatial",
        "prompt": "How do I create 3D Tiles from a 3DGS model for web visualization?",
        "chosen": """**3D Tiles from 3DGS:**

**3D Tiles = OGC standard for streaming massive 3D datasets** (Cesium, deck.gl, MapBox)

**Convert to mesh, then tile:**
```python
def gaussians_to_3dtiles(gaussians, bounds, output_dir, tile_size=100):
    mesh = extract_mesh_from_gaussians(gaussians)
    tiles = spatial_partition_mesh(mesh, bounds, tile_size)
    tileset = create_tileset(tiles, bounds)
    write_tileset(tileset, output_dir)

def create_tileset(tiles, bounds):
    return {
        "asset": {"version": "1.0", "generator": "Orb 3DGS"},
        "geometricError": 500,
        "root": {
            "boundingVolume": {"region": [rad_west, rad_south, rad_east, rad_north, min_z, max_z]},
            "geometricError": 100,
            "refine": "REPLACE",
            "children": [{"boundingVolume": t.bv, "geometricError": 10,
                         "content": {"uri": f"tile_{i}/content.glb"}} for i, t in enumerate(tiles)]
        }
    }
```

**Direct Gaussian splatting in browser:** gsplat.js or similar WebGL library

**Cesium integration:**
```html
<script>
const tileset = viewer.scene.primitives.add(
    new Cesium.Cesium3DTileset({url: './tileset/tileset.json'})
);
viewer.zoomTo(tileset);
</script>
```""",
        "rejected": "Convert 3DGS to mesh, partition spatially, export each tile as glTF, and create tileset.json for Cesium to consume."
    },
    {
        "category": "geospatial",
        "prompt": "How do I handle different vertical datums in 3DGS georeferencing?",
        "chosen": """**Vertical datum management:**

**Common datums:**

| Datum | Description |
|-------|-------------|
| WGS84 Ellipsoid | Geometric height (GPS raw) |
| EGM96 | Geoid model (legacy) |
| EGM2008 | Current geoid standard |
| NAVD88 | North American MSL |

**The problem:**
```
GPS: h = 100m (ellipsoidal)
Map: H = 75m (orthometric)
Difference: N = h - H = 25m (geoid undulation)
```

**Conversion:**
```python
from pyproj import CRS, Transformer

class VerticalDatumConverter:
    def ellipsoid_to_orthometric(self, lat, lon, h_ellipsoid, geoid='EGM2008'):
        N = self.get_geoid_undulation(lat, lon, geoid)
        return h_ellipsoid - N
    
    def orthometric_to_ellipsoid(self, lat, lon, H_orthometric, geoid='EGM2008'):
        N = self.get_geoid_undulation(lat, lon, geoid)
        return H_orthometric + N
```

**Apply to 3DGS:**
```python
def georeference_3dgs_with_vertical(gaussians, gcps, target_datum='EGM2008'):
    # Ensure GCPs in target datum
    for gcp in gcps:
        if gcp['vertical_datum'] != target_datum:
            gcp['z'] = convert_vertical(gcp['lat'], gcp['lon'], gcp['z'],
                                        gcp['vertical_datum'], target_datum)
    transform = compute_7_param_transform(gcps)
    gaussians = apply_transform(gaussians, transform)
    gaussians.metadata['vertical_datum'] = target_datum
```

**Best practices:** Document datum, use EGM2008, store ellipsoidal internally, convert for display.""",
        "rejected": "Convert between ellipsoidal (GPS) and orthometric (geoid) heights using the geoid undulation value for your location."
    },
    {
        "category": "geospatial",
        "prompt": "How do I perform terrain analysis for route planning?",
        "chosen": """**Terrain analysis for route planning:**

**Key factors:**

| Factor | Metric | Threshold |
|--------|--------|-----------|
| Slope | Degrees | <15° vehicles, <30° dismounted |
| Surface | Classification | Avoid water, dense vegetation |
| Obstacles | Height | Based on vehicle clearance |

**Cost surface generation:**
```python
def generate_cost_surface(dem, landcover, resolution):
    slope = compute_slope(dem, resolution)
    
    # Base cost from slope
    cost = np.where(slope < 5, 1, np.where(slope < 15, 2, 
                   np.where(slope < 30, 5, 100)))
    
    # Modify by landcover
    cost = np.where(landcover == 'water', 1000, cost)
    cost = np.where(landcover == 'forest', cost * 2, cost)
    cost = np.where(landcover == 'road', 0.5, cost)
    
    return cost
```

**Least-cost path:**
```python
from skimage.graph import route_through_array

def find_optimal_route(cost_surface, start, end):
    path, cost = route_through_array(cost_surface, start, end, fully_connected=True)
    return np.array(path), cost
```

**Corridor analysis:**
```python
def compute_mobility_corridor(cost_surface, start, end, width_cells=10):
    paths = []
    for offset in range(-width_cells//2, width_cells//2):
        path, _ = find_optimal_route(cost_surface, start + [0, offset], end)
        paths.append(path)
    return combine_paths_to_corridor(paths)
```

**Output:** Route polyline, corridor polygon, waypoints with elevation profile""",
        "rejected": "Generate a cost surface from slope and landcover, then use least-cost path algorithms to find optimal routes."
    },
    {
        "category": "geospatial",
        "prompt": "How do I export 3DGS for use in flight simulators?",
        "chosen": """**Flight simulator export from 3DGS:**

**Target formats:**

| Simulator | Format | Notes |
|-----------|--------|-------|
| DCS World | Custom terrain | EDM/LOD models |
| X-Plane | DSF scenery | Orthophoto + mesh |
| MSFS | glTF + BGL | SDK required |
| Prepar3D | BGL | Similar to MSFS |

**General workflow:**
```python
def export_for_flightsim(gaussians, bounds, output_dir, target='xplane'):
    # 1. Generate terrain mesh
    mesh = extract_mesh_from_gaussians(gaussians)
    mesh_simplified = simplify_mesh(mesh, target_faces=100000)
    
    # 2. Generate orthophoto texture
    ortho = generate_ortho_from_3dgs(gaussians, bounds, gsd=0.5)
    
    # 3. Generate DEM for elevation
    dem = gaussians_to_dsm(gaussians, bounds, resolution=10)
    
    # 4. Export in target format
    if target == 'xplane':
        export_xplane_dsf(mesh_simplified, ortho, dem, output_dir)
    elif target == 'msfs':
        export_msfs_package(mesh_simplified, ortho, dem, output_dir)
```

**X-Plane DSF export:**
```python
def export_xplane_dsf(mesh, ortho, dem, output_dir):
    # Create terrain mesh
    mesh.export(f'{output_dir}/terrain.obj')
    # Save orthophoto as DDS
    save_dds(ortho, f'{output_dir}/ortho.dds')
    # Create DSF scenery package structure
    create_dsf_package(output_dir)
```

**LOD considerations:** Multiple mesh resolutions for distance-based rendering

**Georeferencing:** Ensure coordinates match simulator's world model (typically WGS84)""",
        "rejected": "Export mesh and orthophoto textures in the format required by your target simulator. Include multiple LOD levels for performance."
    },
]

