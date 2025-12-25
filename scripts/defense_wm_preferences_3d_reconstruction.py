# 3D Reconstruction preferences (13 items)
RECONSTRUCTION_PREFS = [
    {
        "category": "3d_reconstruction",
        "prompt": "What is 3D Gaussian Splatting and how does it differ from NeRF?",
        "chosen": """**3D Gaussian Splatting (3DGS)** represents scenes as collections of 3D Gaussian primitives, each with position, covariance, opacity, and spherical harmonic coefficients for view-dependent color.

**Key differences from NeRF:**

| Aspect | 3DGS | NeRF |
|--------|------|------|
| Representation | Explicit (Gaussian primitives) | Implicit (MLP weights) |
| Rendering | Rasterization (tile-based splatting) | Ray marching (volume rendering) |
| Training speed | ~15-30 min | Hours to days |
| Inference speed | 100+ FPS real-time | 0.1-5 FPS (slow) |
| Memory | Higher (stores Gaussians) | Lower (compact MLP) |
| Editability | Direct manipulation | Requires retraining |

**3DGS pipeline:**
1. **Initialization:** SfM point cloud (COLMAP) seeds Gaussian positions
2. **Optimization:** Differentiable rasterizer backprops photometric loss
3. **Densification:** Clone/split Gaussians in high-gradient regions
4. **Pruning:** Remove low-opacity or large Gaussians

**Defense applications:** 3DGS excels for ISR where real-time rendering of captured environments is critical—drone-captured terrain, facility reconstruction, mission rehearsal.""",
        "rejected": "3D Gaussian Splatting uses Gaussians instead of neural networks like NeRF. It's faster for rendering but uses more memory."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "How do I generate a 3D model from a single image?",
        "chosen": """**Single-image 3D reconstruction pipeline:**

**Stage 1: Depth Estimation**
- Model: Depth Anything V2 or MiDaS
- Output: Dense depth map (relative or metric)

**Stage 2: Multi-view Synthesis**
- Model: Zero123++ or SV3D (Stable Video 3D)
- Output: 6-12 novel views at canonical poses

**Stage 3: 3D Reconstruction**
- Option A: Feed synthesized views to 3DGS
- Option B: Direct 3D generation (LRM, One-2-3-45++)

**Stage 4: Refinement**
- Texture enhancement, geometry regularization, scale calibration

```python
from depth_anything import DepthAnythingV2
from zero123 import Zero123PlusPlus
from gsplat import GaussianSplatting

depth_model = DepthAnythingV2.load("vits")
depth_map = depth_model.infer(image)

mv_model = Zero123PlusPlus.load()
views = mv_model.generate(image, num_views=12)

gs = GaussianSplatting()
gs.train(views, depth_prior=depth_map, iterations=7000)
gs.export("output.ply")
```

**Quality expectations:** Single-image reconstruction is ill-posed. Expect plausible geometry, not ground-truth accuracy.""",
        "rejected": "Use a depth estimation model to get depth, then convert to 3D. Models like Zero123 can help generate additional views."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "What is COLMAP and why is it important for 3DGS?",
        "chosen": """**COLMAP = Structure-from-Motion (SfM) + Multi-View Stereo (MVS) pipeline**

**Role in 3DGS:** Provides initialization data:
1. **Camera poses** (extrinsics): Position and orientation per image
2. **Camera intrinsics:** Focal length, principal point, distortion
3. **Sparse point cloud:** Initial 3D points to seed Gaussians

**COLMAP pipeline stages:**

| Stage | Output | Purpose |
|-------|--------|---------|
| Feature extraction | SIFT keypoints | Detect distinctive points |
| Feature matching | Correspondence pairs | Link points across views |
| Sparse reconstruction | Cameras + points | Geometric structure |

```bash
colmap feature_extractor --database_path db.db --image_path ./images
colmap exhaustive_matcher --database_path db.db
colmap mapper --database_path db.db --image_path ./images --output_path ./sparse
colmap model_converter --input_path ./sparse/0 --output_path ./sparse/0 --output_type TXT
```

**Output files for 3DGS:**
- `cameras.txt`: Intrinsic parameters
- `images.txt`: Extrinsic poses
- `points3D.txt`: Sparse point cloud (seeds Gaussians)

**Failure modes:** Poor texture, repetitive patterns, insufficient overlap, motion blur.""",
        "rejected": "COLMAP does Structure from Motion to get camera poses and a point cloud. 3DGS needs this to initialize the Gaussians."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "How do I optimize 3DGS training for large-scale outdoor scenes?",
        "chosen": """**Large-scale 3DGS optimization strategies:**

**1. Hierarchical partitioning**
- Divide scene into spatial blocks
- Train per-block 3DGS models
- Merge with overlap blending

**2. Level-of-detail (LOD)**
```python
def compute_lod_scale(gaussian_pos, camera_pos, base_scale):
    distance = np.linalg.norm(gaussian_pos - camera_pos)
    if distance > 100:
        return base_scale * 2.0  # Far field: larger, fewer
    elif distance > 50:
        return base_scale * 1.5
    return base_scale  # Near field: full detail
```

**3. Memory optimization**

| Technique | VRAM Savings | Trade-off |
|-----------|--------------|-----------|
| FP16 training | 40-50% | Minor quality loss |
| Gradient checkpointing | 30-40% | Slower training |
| Aggressive pruning | 20-30% | Detail loss |

**4. Training config for outdoor:**
```python
training_config = {
    "iterations": 30000,
    "densify_until_iter": 15000,
    "position_lr_init": 0.00016,
    "percent_dense": 0.01,  # Lower for outdoor
}
```

**5. Sky handling:** Mask sky regions (SAM2), use environment map for background.""",
        "rejected": "For large scenes, split into chunks and train separately. Use lower resolution or fewer Gaussians to fit in memory."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "What metrics should I use to evaluate 3DGS reconstruction quality?",
        "chosen": """**3DGS quality metrics:**

**1. Image-based metrics (primary):**

| Metric | Range | Target |
|--------|-------|--------|
| PSNR | 0-∞ dB | >30 good, >35 excellent |
| SSIM | 0-1 | >0.95 good |
| LPIPS | 0-1 | <0.1 good (lower better) |

**2. Geometric metrics (if GT available):**

| Metric | Measures |
|--------|----------|
| Chamfer Distance | Point cloud similarity |
| F-score | Accuracy + completeness |
| Depth RMSE | Depth map accuracy |

**3. Efficiency metrics:**
- FPS (>30 real-time)
- Gaussian count
- Model size (MB)

```python
from torchmetrics.image import PeakSignalNoiseRatio, StructuralSimilarityIndexMeasure
from torchmetrics.image.lpip import LearnedPerceptualImagePatchSimilarity

def evaluate_reconstruction(rendered, ground_truth):
    psnr = PeakSignalNoiseRatio(data_range=1.0)
    ssim = StructuralSimilarityIndexMeasure(data_range=1.0)
    lpips = LearnedPerceptualImagePatchSimilarity(net_type='alex')
    return {
        "psnr": psnr(rendered, ground_truth).item(),
        "ssim": ssim(rendered, ground_truth).item(),
        "lpips": lpips(rendered, ground_truth).item(),
    }
```

**Defense context:** Prioritize LPIPS (perceptual for analysts) and geometric accuracy.""",
        "rejected": "Use PSNR and SSIM to measure quality. Higher PSNR and SSIM values mean better reconstruction."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "How do I handle dynamic objects in 3DGS reconstruction?",
        "chosen": """**Dynamic object handling strategies:**

**1. Masking approach (remove dynamics)**
```python
from sam2 import SAM2VideoPredictor

predictor = SAM2VideoPredictor.load("sam2_hiera_large")
masks = predictor.segment_video(video_frames, prompts=["person", "vehicle"])

for frame, mask in zip(frames, masks):
    static_frame = frame * (1 - mask)  # Zero out dynamic regions
```

**2. Per-frame Gaussians (4D Gaussian Splatting)**

| Method | Approach | Trade-off |
|--------|----------|-----------|
| Dynamic 3DGS | Position MLP over time | Memory intensive |
| 4D-GS | 4D Gaussian primitives | Training complexity |
| Deformable 3DGS | Canonical + deformation | Quality for non-rigid |

**3. Temporal consistency filtering**
```python
def compute_static_mask(frames, threshold=0.1):
    mean_frame = np.mean(frames, axis=0)
    variance = np.var(frames, axis=0)
    return variance < threshold
```

**4. Multi-stage reconstruction**
1. Reconstruct static background
2. Extract dynamics via differencing
3. Reconstruct dynamics separately
4. Composite layers

**Defense application:** Mask vehicles/personnel for terrain reconstruction. Use 4D-GS only if motion capture required.""",
        "rejected": "Use segmentation to mask out moving objects before reconstruction, or use 4D Gaussian Splatting for dynamic scenes."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "What is the gsplat library and how does it compare to other 3DGS implementations?",
        "chosen": """**gsplat = High-performance CUDA kernels for 3D Gaussian Splatting**

Developed by Nerfstudio team. Focus: Speed, modularity, research flexibility.

**Comparison:**

| Implementation | Speed | Flexibility | Maintenance |
|----------------|-------|-------------|-------------|
| gsplat | Fastest | High (modular) | Active |
| gaussian-splatting (original) | Fast | Low | Limited |
| nerfstudio | Medium | High | Active |
| taichi-3dgs | Medium | Medium | Community |

**Key advantages:**
1. **Modular rasterizer:** Swap components easily
2. **Memory efficient:** Better gradient handling
3. **Research-ready:** Easy to extend
4. **Compression:** Built-in quantization

```python
import torch
from gsplat import rasterization

rendered, alpha, info = rasterization(
    means=gaussian_means,      # (N, 3)
    quats=gaussian_quats,      # (N, 4)
    scales=gaussian_scales,    # (N, 3)
    opacities=gaussian_opacities,
    colors=gaussian_colors,
    viewmats=camera_poses,     # (C, 4, 4)
    Ks=camera_intrinsics,      # (C, 3, 3)
    width=width, height=height,
)
```

**For Orb platform:** gsplat recommended for modular RSI pipeline.""",
        "rejected": "gsplat is a CUDA library for Gaussian Splatting. It's faster than some alternatives and actively maintained."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "How do I convert 3DGS output to mesh for CAD/GIS integration?",
        "chosen": """**3DGS to mesh conversion pipeline:**

**Method 1: Poisson Surface Reconstruction**
```python
import open3d as o3d

def gaussians_to_mesh(gaussian_means, gaussian_colors, gaussian_opacities):
    valid = gaussian_opacities > 0.5
    points = gaussian_means[valid]
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(gaussian_colors[valid])
    pcd.estimate_normals()
    pcd.orient_normals_consistent_tangent_plane(k=15)
    
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=10)
    vertices_to_remove = densities < np.quantile(densities, 0.05)
    mesh.remove_vertices_by_mask(vertices_to_remove)
    return mesh
```

**Method 2: Marching Cubes on opacity field**

**Method 3: SuGaR** (Surface-Aligned Gaussians) - constrains to surfaces

**Export formats:**

| Format | Use Case |
|--------|----------|
| OBJ | CAD software |
| PLY | Point cloud tools |
| GLTF/GLB | Web/game engines |
| GeoTIFF | GIS (with georeferencing) |
| LAS/LAZ | LiDAR workflows |

**GIS integration requires:** Ground control points for coordinate transformation.""",
        "rejected": "Use Poisson reconstruction to convert the Gaussian point cloud to a mesh. Export as OBJ for CAD or add georeferencing for GIS."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "What camera configurations work best for 3DGS capture?",
        "chosen": """**Optimal capture configurations for 3DGS:**

**1. Overlap requirements:**

| Scene Type | Overlap | View Count |
|------------|---------|------------|
| Object (turntable) | 80%+ | 50-100 |
| Indoor room | 70%+ | 100-300 |
| Outdoor small | 60%+ | 200-500 |
| Large-scale | 50%+ | 500+ |

**2. Key parameters:**

| Parameter | Recommendation |
|-----------|----------------|
| Shutter speed | >1/500s (drone), >1/125s (handheld) |
| Aperture | f/5.6 - f/11 |
| ISO | Lowest acceptable |
| Resolution | ≥12MP |

**3. Problematic conditions:**

| Condition | Mitigation |
|-----------|------------|
| Specular surfaces | Polarizing filter, overcast |
| Transparent objects | Mask or avoid |
| Textureless regions | Add temporary markers |
| Moving objects | Mask or reshoot |

**4. Drone-specific (ISR):**
```python
capture_plan = {
    "altitude_m": [50, 75, 100],
    "overlap_forward": 0.80,
    "overlap_side": 0.70,
    "gimbal_angles": [-90, -45],  # Nadir + oblique
}
```

**Validation:** Run COLMAP first. If it fails, capture is insufficient.""",
        "rejected": "Use high overlap (70%+) and capture from multiple angles. Avoid blurry images and moving objects."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "How do I handle textureless regions in 3DGS?",
        "chosen": """**Textureless region challenges and solutions:**

**Problem:** COLMAP feature matching fails → no poses → no initialization.

**Affected surfaces:** Walls, floors, sky, water, snow, uniform materials.

**Solution 1: Depth priors**
```python
from depth_anything import DepthAnythingV2

def depth_regularization_loss(rendered_depth, mono_depth, mask):
    scale = torch.median(rendered_depth[mask]) / torch.median(mono_depth[mask])
    aligned_mono = mono_depth * scale
    return F.l1_loss(rendered_depth[mask], aligned_mono[mask])
```

**Solution 2: Geometric priors (planar regularization)**
```python
def planar_loss(gaussian_means, plane_mask):
    plane_points = gaussian_means[plane_mask]
    centroid = plane_points.mean(dim=0)
    _, _, Vh = torch.linalg.svd(plane_points - centroid)
    normal = Vh[-1]
    distances = torch.abs((plane_points - centroid) @ normal)
    return distances.mean()
```

**Solution 3: Multi-modal fusion**

| Sensor | Contribution |
|--------|--------------|
| RGB | Texture, color |
| LiDAR | Geometry in textureless areas |
| Thermal | Edge detection |

**Solution 4: Capture modification**
- Add temporary texture (chalk, tape)
- Change lighting angle

**Priority for defense:** LiDAR fusion most robust for operational environments.""",
        "rejected": "Textureless areas are hard for feature matching. Use depth estimation or add texture markers if possible."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "What is the difference between NeRF, 3DGS, and photogrammetry?",
        "chosen": """**Comparison of 3D reconstruction approaches:**

| Aspect | Photogrammetry | NeRF | 3DGS |
|--------|---------------|------|------|
| **Representation** | Explicit mesh | Implicit MLP | Explicit Gaussians |
| **Output** | Mesh, ortho | Novel views | Novel views, point cloud |
| **Training** | Hours | Hours-days | 15-30 min |
| **Rendering** | Real-time | 0.1-5 FPS | 100+ FPS |
| **Metric accuracy** | Best | Variable | Variable |
| **View synthesis** | Limited | Excellent | Excellent |

**When to use each:**

**Photogrammetry:** Surveying, measurement, CAD/GIS integration, formal products

**NeRF:** Highest quality archival, reflective objects, research

**3DGS:** Real-time visualization, mission rehearsal, rapid turnaround

**Pipeline comparison:**
```
Photogrammetry: Images → SfM → Dense MVS → Mesh → Texture (hours)
NeRF:          Images → SfM → NeRF Training → Render (hours-days)
3DGS:          Images → SfM → 3DGS Training → Real-time (30 min)
```

**Defense recommendation:** 3DGS for operational tempo, photogrammetry for formal products.""",
        "rejected": "Photogrammetry makes meshes, NeRF uses neural networks, and 3DGS uses Gaussians. 3DGS is fastest for rendering."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "How do I scale 3DGS to city-scale reconstruction?",
        "chosen": """**City-scale 3DGS architecture:**

| Scale | Images | Gaussians | Approach |
|-------|--------|-----------|----------|
| Building | 100-500 | 1-5M | Single model |
| Block | 500-2K | 5-20M | Optimized single |
| Neighborhood | 2K-10K | 20-100M | Partitioned |
| City | 10K-100K+ | 100M+ | Hierarchical |

**Hierarchical approach:**
```python
class CityScaleReconstructor:
    def __init__(self, bounds, tile_size=100):
        self.tiles = self.partition_space(bounds, tile_size)
        
    def assign_images_to_tiles(self, images, poses):
        for img, pose in zip(images, poses):
            for tile in self.tiles:
                if tile.contains(pose.position):
                    tile.add_image(img, pose)
    
    def train_parallel(self, num_gpus=4):
        with ProcessPoolExecutor(max_workers=num_gpus) as executor:
            futures = {executor.submit(train_tile, tile): tile 
                      for tile in self.tiles}
```

**LOD streaming for rendering:**
```python
def render_city(camera, tile_models, budget=5_000_000):
    visible_tiles = frustum_cull(camera, tile_models)
    sorted_tiles = sort_by_distance(camera, visible_tiles)
    gaussians_rendered = 0
    for tile in sorted_tiles:
        if gaussians_rendered > budget: break
        render(tile.get_gaussians(compute_lod(camera, tile)))
```

**Storage:** Separate .ply per tile, octree spatial queries, load on demand.""",
        "rejected": "Split the city into tiles, train each tile separately, then merge them. Use LOD for rendering large areas."
    },
    {
        "category": "3d_reconstruction",
        "prompt": "How do I add semantic labels to 3DGS reconstructions?",
        "chosen": """**Semantic 3DGS pipeline:**

**Step 1: Segment training images**
```python
from transformers import AutoProcessor, AutoModelForUniversalSegmentation

processor = AutoProcessor.from_pretrained("facebook/mask2former-swin-large-ade-semantic")
model = AutoModelForUniversalSegmentation.from_pretrained("facebook/mask2former-swin-large-ade-semantic")

def segment_images(images):
    segmentations = []
    for img in images:
        inputs = processor(images=img, return_tensors="pt")
        outputs = model(**inputs)
        seg = processor.post_process_semantic_segmentation(outputs)[0]
        segmentations.append(seg)
    return segmentations
```

**Step 2: Extend Gaussian representation**
```python
class SemanticGaussian:
    position = torch.zeros(3)
    sh_coeffs = torch.zeros(48)  # Color
    semantic_logits = torch.zeros(num_classes)  # NEW
```

**Step 3: Train with semantic loss**
```python
def training_step(gaussians, gt_image, gt_semantics, camera):
    rendered_rgb, rendered_sem = render(gaussians, camera)
    rgb_loss = l1_loss(rendered_rgb, gt_image)
    sem_loss = F.cross_entropy(rendered_sem, gt_semantics)
    return rgb_loss + 0.1 * sem_loss
```

**Defense applications:**

| Class | Use Case |
|-------|----------|
| Building | Infrastructure mapping |
| Vehicle | Activity detection |
| Vegetation | Concealment analysis |
| Road | Route planning |

**Output:** Each Gaussian has class probability vector for filtered rendering.""",
        "rejected": "Segment the training images with a model like Mask2Former, then add semantic features to the Gaussians during training."
    },
]

