# ISR Analysis preferences (12 items)
ISR_PREFS = [
    {
        "category": "isr_analysis",
        "prompt": "What is the Intelligence Cycle and how does ISR feed into it?",
        "chosen": """**Intelligence Cycle (JIPOE process):**

```
Planning & Direction → Collection → Processing → Analysis → Dissemination
       ↑                                                          │
       └──────────────────────────────────────────────────────────┘
```

**ISR = Intelligence, Surveillance, Reconnaissance**

| Component | Definition | Assets |
|-----------|------------|--------|
| Intelligence | Processed info for decisions | Fusion centers |
| Surveillance | Persistent observation | Satellites, fixed sensors |
| Reconnaissance | Directed collection | Drones, manned aircraft |

**ISR contribution to each phase:**

1. **Planning:** ISR capabilities inform collection requirements
2. **Collection:** EO/IR imagery, SAR/GMTI radar, SIGINT
3. **Processing:** Imagery exploitation, 3D reconstruction (Orb)
4. **Analysis:** Pattern detection, change detection, target development
5. **Dissemination:** Imagery products, 3D scene models

**Orb platform role:** Processing phase—transforms raw ISR imagery into exploitable 3D scene models.""",
        "rejected": "The Intelligence Cycle has five phases: planning, collection, processing, analysis, and dissemination. ISR collects data that feeds into this cycle."
    },
    {
        "category": "isr_analysis",
        "prompt": "What is GEOINT and how does it relate to IMINT?",
        "chosen": """**GEOINT = Geospatial Intelligence**

Exploitation and analysis of imagery and geospatial information to describe physical features and geographically referenced activities.

**GEOINT = IMINT + GEOSPATIAL INFORMATION + ANALYSIS**

| Discipline | Source | Output |
|------------|--------|--------|
| IMINT | EO/IR, SAR sensors | Annotated imagery |
| GEOSPATIAL | Maps, DEMs | Terrain products |
| Analysis | Fusion | Assessments, predictions |

**IMINT vs GEOINT:**

| Aspect | IMINT | GEOINT |
|--------|-------|--------|
| Focus | What's in image | Spatial context + imagery |
| Output | Imagery reports | Fused geospatial products |
| Scope | Single-source | Multi-source fusion |

**GEOINT products:**
- **Foundation:** Topographic maps, DEMs, CIB
- **Thematic:** Infrastructure analysis, LOC, obstacles
- **Dynamic:** Activity tracking, change detection

**Key standards:** NGA NSG standards, NITF/NSIF for imagery, GeoTIFF for rasters, GML/GeoJSON for vectors""",
        "rejected": "GEOINT combines imagery intelligence (IMINT) with geospatial data for location-based analysis. IMINT is just the imagery part."
    },
    {
        "category": "isr_analysis",
        "prompt": "How do I detect changes between two 3DGS reconstructions?",
        "chosen": """**3DGS change detection pipeline:**

**Approach 1: Rendered image differencing**
```python
def render_based_change_detection(gs_before, gs_after, cameras):
    changes = []
    for camera in cameras:
        img_before = render(gs_before, camera)
        img_after = render(gs_after, camera)
        diff = compute_ssim_map(img_before, img_after)
        change_mask = diff < 0.8
        changes.append({'camera': camera, 'change_mask': change_mask})
    return changes
```

**Approach 2: Gaussian-space differencing**
```python
def gaussian_space_change_detection(gs_before, gs_after, threshold=0.5):
    tree_before = KDTree(gs_before.means.cpu().numpy())
    changes = {'added': [], 'removed': [], 'modified': []}
    
    for i, pos in enumerate(gs_after.means):
        dist, idx = tree_before.query(pos.cpu().numpy())
        if dist > threshold:
            changes['added'].append(i)
        else:
            color_diff = torch.norm(gs_after.colors[i] - gs_before.colors[idx])
            if color_diff > 0.1:
                changes['modified'].append((i, idx))
    return changes
```

**Output products:**
- Change heatmap (probability per location)
- Change vectors (object-level added/removed/moved)
- Change report with imagery

**ISR application:** Construction activity, vehicle staging, infrastructure damage.""",
        "rejected": "Compare renders from the same viewpoints or match Gaussians by position. Flag differences above a threshold as changes."
    },
    {
        "category": "isr_analysis",
        "prompt": "What is SAR imagery and how does it complement optical for 3D reconstruction?",
        "chosen": """**SAR = Synthetic Aperture Radar** (active sensor, microwave pulses)

**SAR vs Optical:**

| Aspect | SAR | Optical |
|--------|-----|---------|
| Illumination | Self-illuminated | Sun-dependent |
| Weather | All-weather | Weather-limited |
| Day/night | 24/7 | Daylight/IR night |
| Interpretation | Requires training | Intuitive |

**SAR modalities:**

| Mode | Measures | Application |
|------|----------|-------------|
| Amplitude | Backscatter | Surface characterization |
| InSAR | Phase difference | DEM generation |
| PolSAR | Polarization | Material classification |
| GMTI | Moving targets | Vehicle detection |

**SAR for 3D reconstruction:**
```python
def fuse_sar_optical_3dgs(optical_images, dem_from_sar):
    colmap_output = run_colmap(optical_images)
    gs = init_gaussians(colmap_output)
    depth_maps = project_dem_to_cameras(dem_from_sar, colmap_output.cameras)
    
    for iter in range(iterations):
        rgb_loss = photometric_loss(gs, optical_images)
        depth_loss = depth_supervision(gs, depth_maps)
        loss = rgb_loss + 0.1 * depth_loss
```

**Benefits:** SAR provides geometry in occluded/shadowed areas, works when optical unavailable, InSAR DEMs are metric-accurate.""",
        "rejected": "SAR uses radar and works through clouds and at night. It can create DEMs that help improve 3D reconstruction geometry."
    },
    {
        "category": "isr_analysis",
        "prompt": "How do I georeference a 3DGS reconstruction?",
        "chosen": """**Georeferencing = Transforming local coordinates to geographic CRS**

**Methods by accuracy:**

| Method | Accuracy | Requirements |
|--------|----------|--------------|
| Image EXIF GPS | 5-20m | GPS-tagged images |
| GNSS RTK | 1-5cm | RTK receiver |
| GCPs | 2-10cm | Surveyed targets |
| LiDAR alignment | 5-50cm | Reference LiDAR |

**GCP-based (most common):**
```python
def compute_transform_gcps(local_points, geo_points):
    # 7-parameter Helmert transformation
    local_centroid = local_points.mean(axis=0)
    geo_centroid = geo_points.mean(axis=0)
    
    local_centered = local_points - local_centroid
    geo_centered = geo_points - geo_centroid
    
    scale = np.sqrt(np.sum(geo_centered**2) / np.sum(local_centered**2))
    
    H = local_centered.T @ geo_centered
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    t = geo_centroid - scale * (R @ local_centroid)
    return R, t, scale

def apply_georef_to_gaussians(gaussians, R, t, scale):
    gaussians.means = scale * (gaussians.means @ R.T) + t
    gaussians.scales = gaussians.scales * scale
```

**CRS recommendation:** Store in WGS84, transform to UTM for measurement, document vertical datum.""",
        "rejected": "Use ground control points to create a transformation from local coordinates to geographic coordinates. Apply to all Gaussians."
    },
    {
        "category": "isr_analysis",
        "prompt": "What is NIIRS and how does it apply to 3DGS outputs?",
        "chosen": """**NIIRS = National Imagery Interpretability Rating Scale** (0-9)

| Level | GSD | Interpretability |
|-------|-----|------------------|
| 4 | 1.2m | Identify buildings |
| 5 | 0.75m | Distinguish vehicle types |
| 6 | 0.4m | Identify vehicles by make |
| 7 | 0.2m | Identify equipment |
| 8 | 0.1m | Identify facial features |

**GIQE equation (simplified):**
```
NIIRS = 10.251 - 3.32·log₁₀(GSD) + 0.656·RER - 0.344·(G/SNR)
```

**Applying to 3DGS:**
```python
def estimate_niirs_rendered(rendered_image, camera_params, ground_elevation):
    altitude = camera_params.position[2] - ground_elevation
    gsd = (altitude * pixel_size_mm) / focal_length_mm
    rer = compute_edge_response(rendered_image)
    snr = compute_snr(rendered_image)
    niirs = 10.251 - 3.32 * np.log10(gsd) + 0.656 * rer - 0.344 / snr
    return min(max(niirs, 0), 9)
```

**Quality preservation:**

| Stage | NIIRS Impact |
|-------|--------------|
| Input imagery | Ceiling |
| 3DGS training | May degrade |
| Rendering | May degrade |
| Compression | Degrades |

**Defense requirement:** Verify 3DGS outputs meet minimum NIIRS before delivery.""",
        "rejected": "NIIRS measures image quality on a 0-9 scale based on what can be interpreted. Higher NIIRS means more detail is visible."
    },
    {
        "category": "isr_analysis",
        "prompt": "How do I integrate 3DGS with mission planning systems?",
        "chosen": """**3DGS mission planning integration:**

**Target systems:**

| System | Format | Use Case |
|--------|--------|----------|
| Falcon View | GeoTIFF, KML | Flight planning |
| ATAK/TAK | CoT, KML | Tactical SA |
| Unity/Unreal | FBX, glTF | Rehearsal |
| Cesium | 3D Tiles | Web visualization |

**Export pipeline:**
```python
class MissionPlanningExporter:
    def export_terrain_geotiff(self, output_path, resolution=1.0):
        dem = self.render_nadir_depth(resolution)
        self.write_geotiff(self.apply_transform(dem), output_path)
    
    def export_kml(self, output_path):
        bounds = self.get_bounds_wgs84()
        kml = f'''<kml><GroundOverlay>
          <Icon><href>ortho.png</href></Icon>
          <LatLonBox><north>{bounds.north}</north>...</LatLonBox>
        </GroundOverlay></kml>'''
    
    def export_unity_scene(self, output_path):
        mesh = self.extract_mesh()
        mesh.export(output_path, format='fbx')
```

**Integration checklist:**
- [ ] Coordinate system matches target
- [ ] Vertical datum documented
- [ ] Scale validated
- [ ] Orientation aligned to true north
- [ ] Timestamp metadata preserved""",
        "rejected": "Export as mesh or GeoTIFF for mission planning systems. Make sure the coordinates are properly georeferenced."
    },
    {
        "category": "isr_analysis",
        "prompt": "What is Activity-Based Intelligence and how can 3DGS support it?",
        "chosen": """**ABI = Activity-Based Intelligence** (patterns over fixed targets)

**Core concepts:**

| Concept | Definition | 3DGS Role |
|---------|------------|-----------|
| Sequence Neutrality | Data valuable regardless of when | Temporal reconstruction |
| Data Before Need | Collect broadly, exploit as needed | Archive 3D snapshots |
| Geo-centricity | Location as primary key | Georeferenced models |

**ABI process:** Observe → Characterize → Discover → Geo-locate → Analyze → Assess

**3DGS ABI pipeline:**
```python
class ABIPipeline:
    def ingest_collection(self, imagery, timestamp):
        gs_model = reconstruct_3dgs(imagery)
        gs_model.timestamp = timestamp
        entities = semantic_segment(gs_model, ['vehicle', 'structure'])
        self.scene_archive[timestamp] = gs_model
        return entities
    
    def detect_activity_patterns(self, tracks, time_window):
        patterns = []
        for track in tracks:
            spatial_cluster = cluster_positions(track.positions)
            temporal_freq = analyze_frequency(track.timestamps)
            if is_significant_pattern(spatial_cluster, temporal_freq):
                patterns.append(Pattern(track, spatial_cluster, temporal_freq))
        return patterns
```

**ABI products from 3DGS:**
- Activity snapshot (3D at point in time)
- Change product (before/after)
- Pattern map (aggregated activity)
- Prediction layer (expected future activity)

**Advantage:** 3DGS provides persistent, navigable archive for retrospective analysis.""",
        "rejected": "ABI focuses on patterns of activity over time. 3DGS can support this by creating temporal snapshots for change detection."
    },
    {
        "category": "isr_analysis",
        "prompt": "How do I detect and track vehicles in 3DGS reconstructions?",
        "chosen": """**Vehicle detection and tracking in 3DGS:**

**Phase 1: Detection in source imagery**
```python
from ultralytics import YOLO
from sam2 import SAM2

def detect_vehicles_in_images(images):
    detector = YOLO('yolov8x.pt')
    segmenter = SAM2.load()
    detections = []
    for i, img in enumerate(images):
        results = detector(img, classes=[2, 5, 7])  # car, bus, truck
        for box in results[0].boxes:
            mask = segmenter.predict(img, box=box.xyxy)
            detections.append({'image_idx': i, 'bbox': box.xyxy, 'mask': mask})
    return detections
```

**Phase 2: Lift to 3D**
```python
def lift_detections_to_3d(detections, gaussians, cameras):
    for det in detections:
        camera = cameras[det['image_idx']]
        projected = project_gaussians(gaussians, camera)
        in_mask = det['mask'][projected.y, projected.x]
        vehicle_idxs = np.where(in_mask)[0]
        det['gaussian_indices'] = vehicle_idxs
        det['centroid'] = gaussians.means[vehicle_idxs].mean(axis=0)
```

**Phase 3: Cluster multi-view detections**
```python
def cluster_vehicle_detections(vehicle_gaussians, threshold=2.0):
    centroids = np.array([v['centroid'] for v in vehicle_gaussians])
    labels = DBSCAN(eps=threshold, min_samples=2).fit_predict(centroids)
    # Merge same-vehicle detections
```

**Phase 4: Temporal tracking** (Hungarian algorithm across snapshots)

**Output:** Vehicle count, locations, movement vectors, activity patterns""",
        "rejected": "Detect vehicles in source images with YOLO, segment with SAM, then project into 3D space based on camera geometry."
    },
    {
        "category": "isr_analysis",
        "prompt": "What is the TCPED process and where does 3DGS fit?",
        "chosen": """**TCPED = Tasking, Collection, Processing, Exploitation, Dissemination**

```
TASKING → PIRs, collection deck, sensor tasking
    ↓
COLLECTION → Satellite passes, UAV sorties
    ↓
PROCESSING → Format conversion, georectification, 3DGS ◄── HERE
    ↓
EXPLOITATION → Imagery analysis, 3D scene exploitation
    ↓
DISSEMINATION → Intel reports, 3D products, mission planning feeds
```

**3DGS in Processing phase:**

| Input | Process | Output |
|-------|---------|--------|
| Raw frames | COLMAP SfM | Camera poses |
| Poses + frames | 3DGS training | Gaussian model |
| Model | Georeferencing | Positioned 3D scene |
| Scene | Quality validation | Exploitation-ready |

**Integration:**
```python
class TCPEDIntegration:
    def process(self, frames):
        colmap_output = run_colmap(frames)
        gaussians = train_3dgs(colmap_output)
        georef = compute_georef(self.collection_metadata['gps'])
        gaussians = apply_georef(gaussians, georef)
        return TCPEDProduct(gaussians=gaussians, quality_report=self.validate())
```

**Key integration points:**
- **Tasking:** Receive PIRs to prioritize quality/speed
- **Collection:** Ingest imagery with metadata chain
- **Exploitation:** Output formats analysts can consume
- **Dissemination:** Export to mission systems""",
        "rejected": "TCPED covers the full ISR workflow. 3DGS fits in the Processing phase, turning collected imagery into 3D products."
    },
    {
        "category": "isr_analysis",
        "prompt": "How do I measure distances and areas in a 3DGS reconstruction?",
        "chosen": """**Mensuration in 3DGS:**

**Prerequisites:** Georeferenced model (known scale and CRS)

**Distance measurement:**
```python
def measure_distance_3d(gaussians, point1_screen, point2_screen, camera):
    ray1 = camera.screen_to_ray(point1_screen)
    ray2 = camera.screen_to_ray(point2_screen)
    hit1 = raycast_gaussians(gaussians, ray1)
    hit2 = raycast_gaussians(gaussians, ray2)
    
    distance = np.linalg.norm(hit1.position - hit2.position)
    return {
        'distance_m': distance,
        'horizontal_distance': np.sqrt((hit1.position[0]-hit2.position[0])**2 + 
                                       (hit1.position[1]-hit2.position[1])**2),
        'vertical_difference': abs(hit1.position[2] - hit2.position[2])
    }
```

**Area measurement:**
```python
def measure_area_3d(gaussians, polygon_screen_points, camera):
    points_3d = [raycast_gaussians(gaussians, camera.screen_to_ray(p)).position 
                 for p in polygon_screen_points]
    # Fit plane, project to 2D, use shoelace formula
    return {'area_m2': area, 'perimeter_m': perimeter}
```

**Volume measurement:** Convex hull of selected Gaussians

**Accuracy considerations:**

| Factor | Impact | Mitigation |
|--------|--------|------------|
| Reconstruction error | 1-5% | Validate with GCPs |
| Ray intersection | Sub-pixel | Use depth buffer |
| Surface noise | Variance | Average samples |""",
        "rejected": "Click two points to measure distance, or draw a polygon for area. The model needs to be georeferenced for real units."
    },
    {
        "category": "isr_analysis",
        "prompt": "What classification levels can 3DGS outputs be processed at?",
        "chosen": """**Classification handling for 3DGS:**

**Derivation principle:** Output ≥ input classification

| Input Source | Typical Classification |
|--------------|----------------------|
| Commercial satellite | Unclassified |
| UAV FMV | Often Unclass/FOUO |
| National technical means | TS/SCI |

**Processing environment:**

| Classification | Environment |
|----------------|------------|
| Unclassified | Standard commercial |
| CUI/FOUO | Controlled, encrypted |
| Secret | SIPRNet |
| TS/SCI | JWICS |

**Classification workflow:**
```python
class ClassifiedProcessingWorkflow:
    def __init__(self, classification_level):
        self.level = classification_level
        assert is_accredited_for(self.level)
        assert no_network_connectivity()  # Air-gapped
        
    def process(self, imagery):
        gaussians = train_3dgs_local(run_colmap_local(imagery))
        gaussians.metadata['classification'] = self.level
        return gaussians
```

**Marking requirements:**
- Classification banner on all products
- Derived from source classification guide
- Declassification date/event
- Handling caveats (NOFORN, REL TO, etc.)

**Orb implication:** HuggingFace deployment only for unclassified. Classified requires accredited infrastructure.""",
        "rejected": "3DGS outputs are classified at the same level as the input imagery. Process classified data only on approved systems."
    },
]

