# Sensor Fusion preferences (12 items)
SENSOR_FUSION_PREFS = [
    {
        "category": "sensor_fusion",
        "prompt": "How do I fuse LiDAR point clouds with 3DGS reconstructions?",
        "chosen": """**LiDAR + 3DGS fusion strategies:**

| LiDAR Strength | 3DGS Strength | Fusion Result |
|----------------|---------------|---------------|
| Metric accuracy | Photorealistic | Accurate + beautiful |
| Works in low texture | Dense color | Complete coverage |
| Night operation | Color info | 24/7 capability |

**Method 1: LiDAR as depth supervision**
```python
def train_3dgs_with_lidar(images, colmap_output, lidar_points, lidar_to_camera):
    gaussians = init_gaussians(colmap_output)
    lidar_depth_maps = {cam_id: project_lidar_to_depth(lidar_points, cam, lidar_to_camera)
                        for cam_id, cam in colmap_output.cameras.items()}
    
    for iteration in range(30000):
        cam_id = sample_camera()
        rendered_rgb, rendered_depth = render(gaussians, cameras[cam_id])
        rgb_loss = l1_loss(rendered_rgb, images[cam_id])
        valid = lidar_depth_maps[cam_id] > 0
        depth_loss = l1_loss(rendered_depth[valid], lidar_depth_maps[cam_id][valid])
        loss = rgb_loss + 0.1 * depth_loss
```

**Method 2: LiDAR as initialization**
```python
def init_gaussians_from_lidar(lidar_points, lidar_colors=None):
    nn = NearestNeighbors(n_neighbors=5).fit(lidar_points)
    distances, _ = nn.kneighbors(lidar_points)
    scales = distances[:, 1:].mean(axis=1) / 2
    gaussians = GaussianModel()
    gaussians.means = torch.tensor(lidar_points)
    gaussians.scales = torch.tensor(scales).unsqueeze(1).repeat(1, 3)
    return gaussians
```

**Method 3: ICP alignment** for post-processing fusion""",
        "rejected": "Use LiDAR points to initialize Gaussians or as depth supervision during training. Align using ICP if captured separately."
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I combine thermal (IR) imagery with visible spectrum for 3DGS?",
        "chosen": """**Thermal + visible 3DGS fusion:**

**Challenges:**

| Challenge | Mitigation |
|-----------|------------|
| Different resolution | Upscale or multi-scale |
| Spectral difference | Feature-agnostic matching |
| Geometric misalignment | Calibrate and register |

**Method 1: Separate reconstruction, joint visualization**
```python
def dual_band_reconstruction(visible_images, thermal_images, calibration):
    colmap_vis = run_colmap(visible_images)
    gs_visible = train_3dgs(colmap_vis)
    thermal_cameras = register_thermal_to_visible(thermal_images, calibration)
    gs_visible.thermal = project_thermal_to_gaussians(gs_visible, thermal_images, thermal_cameras)
    return gs_visible
```

**Method 2: Multi-spectral training**
```python
class MultiSpectralGaussian(nn.Module):
    rgb_sh = nn.Parameter(torch.zeros(n_points, 48))
    thermal = nn.Parameter(torch.zeros(n_points, 1))

def train_multispectral(gaussians, visible_images, thermal_images, cameras):
    for iteration in range(30000):
        rendered_rgb = render_rgb(gaussians, cameras[cam])
        rendered_thermal = render_thermal(gaussians, cameras[cam])
        loss = l1_loss(rendered_rgb, visible_images[cam]) + 0.3 * l1_loss(rendered_thermal, thermal_images[cam])
```

**Visualization:**
```python
def render_multiband(gaussians, camera, mode='fusion'):
    if mode == 'fusion':
        rgb = render_rgb(gaussians, camera)
        thermal = render_thermal(gaussians, camera)
        return 0.7 * rgb + 0.3 * apply_colormap(thermal, 'jet')
```""",
        "rejected": "Build 3DGS from visible images, then project thermal imagery onto the model to add temperature data as an additional attribute."
    },
    {
        "category": "sensor_fusion",
        "prompt": "What is image registration and why is it critical for multi-sensor fusion?",
        "chosen": """**Image registration = Aligning images from different sources to common frame**

**Why critical:** Without registration → misaligned features, blurry results, wrong geometry, failed COLMAP

**Registration types:**

| Type | DOF | Use Case |
|------|-----|----------|
| Rigid | 6 | Same sensor, different poses |
| Similarity | 7 | Different focal lengths |
| Affine | 12 | Moderate distortion |
| Projective | 8 | Planar scenes |

**Feature-based:**
```python
def register_images_features(source, target, method='sift'):
    detector = cv2.SIFT_create()
    kp1, desc1 = detector.detectAndCompute(source, None)
    kp2, desc2 = detector.detectAndCompute(target, None)
    matches = cv2.BFMatcher(cv2.NORM_L2).knnMatch(desc1, desc2, k=2)
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]
    H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    return cv2.warpPerspective(source, H, target.shape[:2][::-1])
```

**Intensity-based (multi-modal):**
```python
def mutual_information(params, source, target):
    transformed = apply_transform(source, params)
    hist_2d = np.histogram2d(target.ravel(), transformed.ravel(), bins=64)[0]
    # Compute MI from joint histogram
    return -mi  # Minimize negative MI
```

**Sensor pairing recommendations:**

| Pair | Best Approach |
|------|---------------|
| Visible-Visible | Feature-based |
| Visible-Thermal | Mutual information |
| Visible-SAR | Learned features |""",
        "rejected": "Image registration aligns images from different sources. Use feature matching for same-modality, mutual information for different modalities."
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I fuse GPS/INS data with visual SLAM for 3DGS?",
        "chosen": """**GPS/INS + Visual fusion for georeferenced 3DGS:**

| Sensor | Strength | Weakness |
|--------|----------|----------|
| GPS | Absolute, global | Noisy, occlusion |
| INS | High rate, smooth | Drifts over time |
| Visual | Rich scene info | Scale ambiguity |

**Loosely-coupled fusion:**
```python
class LooseCoupledFusion:
    def __init__(self):
        self.kf = KalmanFilter(dim_x=9, dim_z=6)  # [x,y,z,vx,vy,vz,r,p,y]
        
    def update_gps(self, gps_position, gps_covariance):
        self.kf.R = np.diag([*np.diag(gps_covariance), 1e6, 1e6, 1e6])
        self.kf.update(np.array([*gps_position, 0, 0, 0]))
        
    def update_visual(self, visual_pose, visual_covariance):
        self.kf.R = visual_covariance
        self.kf.update(visual_pose)
```

**Tightly-coupled (factor graph with GTSAM):**
- Visual odometry factors (relative pose)
- GPS factors (absolute position)
- IMU factors (between poses)
- Joint optimization via Levenberg-Marquardt

**COLMAP with GPS priors:**
```python
def run_colmap_with_gps_prior(images, gps_positions):
    for img_path, gps in zip(images, gps_positions):
        database.update_image_prior_position(image_id, prior_position=gps['position'])
    reconstruction = pycolmap.incremental_mapping(database_path, image_path, output_path)
```

**Result:** Georeferenced camera poses with metric scale for 3DGS training.""",
        "rejected": "Use a Kalman filter to combine GPS positions, INS orientation, and visual odometry. This gives georeferenced camera poses for 3DGS."
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I handle temporal synchronization between multiple sensors?",
        "chosen": """**Temporal synchronization for multi-sensor 3DGS:**

**Challenges:** Clock drift, latency, different rates, jitter

**Hardware sync (best):** Master clock triggering all sensors via PPS

**Software synchronization:**
```python
class TemporalSynchronizer:
    def estimate_offset(self, sensor1, sensor2, method='correlation'):
        signal1 = self.extract_motion_signal(sensor1)
        signal2 = self.extract_motion_signal(sensor2)
        correlation = np.correlate(signal1, signal2, mode='full')
        lag = np.argmax(correlation) - len(signal1) + 1
        return lag * dt
    
    def interpolate_to_reference(self, sensor_name):
        ref_times = self.data_streams[self.reference]['timestamps']
        sensor_times = self.data_streams[sensor_name]['timestamps'] + self.time_offsets[sensor_name]
        return interp1d(sensor_times, sensor_data, axis=0)(ref_times)
```

**Handling different frame rates:**
```python
def resample_to_common_rate(streams, target_rate=30):
    t_min = max(s['timestamps'][0] for s in streams.values())
    t_max = min(s['timestamps'][-1] for s in streams.values())
    common_times = np.linspace(t_min, t_max, int((t_max - t_min) * target_rate))
    return {name: interp1d(s['timestamps'], s['data'])(common_times) for name, s in streams.items()}
```

**Frame association:**
```python
def associate_frames(camera_times, lidar_times, max_offset=0.05):
    associations = []
    for i, cam_t in enumerate(camera_times):
        nearest = np.argmin(np.abs(lidar_times - cam_t))
        if abs(lidar_times[nearest] - cam_t) < max_offset:
            associations.append({'camera': i, 'lidar': nearest})
    return associations
```""",
        "rejected": "Estimate time offsets between sensors using cross-correlation of motion signals, then interpolate all data to common timestamps."
    },
    {
        "category": "sensor_fusion",
        "prompt": "What is the difference between early, late, and mid-level fusion?",
        "chosen": """**Fusion level taxonomy:**

**Early Fusion (Data Level):** Concatenate raw data before processing
**Mid-Level (Feature Level):** Extract features separately, fuse features
**Late Fusion (Decision Level):** Process independently, merge outputs

| Aspect | Early | Mid | Late |
|--------|-------|-----|------|
| Complexity | High | Medium | Low |
| Info preservation | Highest | High | Lower |
| Flexibility | Low | Medium | High |
| Robustness | Lower | Medium | Higher |

**Early fusion example:**
```python
def early_fusion_3dgs(rgb, thermal, depth):
    fused = np.concatenate([rgb, thermal[:,:,None], depth[:,:,None]], axis=2)
    return train_multichannel_3dgs(fused)
```

**Mid-level fusion example:**
```python
def mid_fusion_3dgs(rgb_images, lidar_points):
    visual_points = run_colmap(rgb_images).points3D
    correspondence = match_features(visual_points, lidar_features)
    fused_points = merge_point_clouds(visual_points, lidar_points, correspondence)
    return train_3dgs(init_gaussians(fused_points))
```

**Late fusion example:**
```python
def late_fusion_3dgs(rgb_images, lidar_points):
    gs_rgb = train_3dgs(run_colmap(rgb_images))
    gs_lidar = init_gaussians_from_lidar(lidar_points)
    transform = compute_alignment(gs_rgb.means, lidar_points)
    return merge_gaussian_models(apply_transform(gs_rgb, transform), gs_lidar)
```

**Recommendation:** Late most robust to calibration errors, early preserves most info.""",
        "rejected": "Early fusion combines raw data, mid-level fuses features, late fusion merges outputs. Late is most robust, early preserves most information."
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I calibrate a multi-camera rig for 3DGS capture?",
        "chosen": """**Multi-camera calibration for 3DGS:**

**Components:** Intrinsics (per-camera), Extrinsics (relative poses), Temporal (sync)

**Intrinsic calibration (checkerboard):**
```python
def calibrate_intrinsics(images, pattern_size=(9, 6), square_size=0.025):
    objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size
    
    for img in images:
        ret, corners = cv2.findChessboardCorners(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), pattern_size)
        if ret:
            obj_points.append(objp)
            img_points.append(cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria))
    
    ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)
    return {'K': K, 'distortion': dist, 'error': ret}
```

**Stereo extrinsic calibration:**
```python
ret, K_l, d_l, K_r, d_r, R, T, E, F = cv2.stereoCalibrate(
    obj_points, img_points_left, img_points_right,
    K_left, dist_left, K_right, dist_right,
    gray.shape[::-1], flags=cv2.CALIB_FIX_INTRINSIC)
# R, T = rotation/translation from left to right
```

**Multi-camera rig:** Calibrate pairs, chain transformations via BFS from reference camera

**Validation:** Triangulate test points, check reprojection error across all cameras (<1 pixel good)""",
        "rejected": "Calibrate each camera's intrinsics with a checkerboard, then stereo calibrate pairs to get extrinsics. Chain transformations for the full rig."
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I use depth sensors (RGB-D) to improve 3DGS reconstruction?",
        "chosen": """**RGB-D enhanced 3DGS:**

**Sensors:** Intel RealSense (~2%), Azure Kinect (~1%), iPhone LiDAR (~1cm)

**Method 1: Depth initialization**
```python
def init_gaussians_from_rgbd(rgb, depth, K, max_depth=10.0):
    u, v = np.meshgrid(np.arange(depth.shape[1]), np.arange(depth.shape[0]))
    valid = (depth > 0) & (depth < max_depth)
    
    z = depth[valid]
    x = (u[valid] - K[0,2]) * z / K[0,0]
    y = (v[valid] - K[1,2]) * z / K[1,1]
    
    points = np.stack([x, y, z], axis=-1)
    colors = rgb[valid] / 255.0
    return init_gaussians(points, colors)
```

**Method 2: Depth supervision**
```python
def train_3dgs_with_depth(images, depth_maps, colmap_output, depth_weight=0.1):
    for iteration in range(30000):
        rendered_rgb, rendered_depth = render_with_depth(gaussians, camera)
        rgb_loss = l1_loss(rendered_rgb, gt_rgb)
        valid = gt_depth > 0
        depth_loss = scale_invariant_depth_loss(rendered_depth[valid], gt_depth[valid])
        loss = rgb_loss + depth_weight * depth_loss
```

**Quality improvements:**

| Metric | RGB-only | RGB-D |
|--------|----------|-------|
| Geometric accuracy | ~5cm | ~1cm |
| Textureless regions | Poor | Good |
| Scale accuracy | Ambiguous | Metric |

**Depth filtering:** Bilateral filter for edge-preserving smoothing""",
        "rejected": "Use depth maps to initialize Gaussians directly or as supervision during training. RGB-D gives metric scale and helps with textureless areas."
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I handle occlusions in multi-view 3DGS reconstruction?",
        "chosen": """**Occlusion handling in 3DGS:**

**Types:** Self-occlusion, inter-object, boundary, dynamic

**Method 1: Visibility-aware training**
```python
def train_3dgs_visibility_aware(gaussians, images, cameras):
    for iteration in range(30000):
        rendered_rgb, alpha, visibility_map = render_with_visibility(gaussians, cameras[cam])
        loss_weight = visibility_map * alpha
        rgb_loss = (torch.abs(rendered_rgb - gt_rgb) * loss_weight).sum() / (loss_weight.sum() + 1e-6)
```

**Method 2: Multi-view consistency**
```python
def enforce_multiview_consistency(gaussians, images, cameras, n_views=3):
    cam_indices = sample_overlapping_cameras(cameras, n_views)
    losses = [l1_loss(render(gaussians, cameras[i]), images[i]) for i in cam_indices]
    consistency_loss = torch.std(torch.stack(losses))
    total_loss = sum(losses) + 0.1 * consistency_loss
```

**Method 3: Occlusion-aware densification**
```python
def densify_occluded_regions(gaussians, images, cameras):
    visibility_count = compute_per_pixel_visibility(gaussians, cameras)
    poorly_visible = visibility_count.sum(dim=0) < (len(cameras) * 0.3)
    # Add Gaussians in poorly visible regions
```

**Method 4: Depth-based reasoning** - Compare rendered depth to GT depth to identify occluded Gaussians

**Method 5: Layered representation** - Multiple Gaussian layers with back-to-front compositing""",
        "rejected": "Track which Gaussians are visible from each view, weight the loss accordingly, and densify in regions that have poor visibility."
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I fuse multiple 3DGS reconstructions of the same scene?",
        "chosen": """**Multi-reconstruction 3DGS fusion:**

**Use cases:** Different sessions, sensors, coverage extension, quality improvement

**Method 1: Rigid alignment and merge**
```python
def align_and_merge_reconstructions(gs_list):
    merged = copy_gaussians(gs_list[0])
    for gs_new in gs_list[1:]:
        # Coarse alignment (RANSAC feature matching)
        result_ransac = o3d.registration.registration_ransac_based_on_feature_matching(...)
        # Fine alignment (ICP)
        result_icp = o3d.registration.registration_icp(pcd_new, pcd_ref, 0.1, result_ransac.transformation)
        gs_aligned = transform_gaussians(gs_new, result_icp.transformation)
        merged = merge_gaussians_dedupe(merged, gs_aligned)
    return merged
```

**Method 2: Overlap-aware blending**
```python
def merge_gaussians_dedupe(gs1, gs2, threshold=0.05, mode='weighted'):
    tree = KDTree(gs1.means.numpy())
    distances, indices = tree.query(gs2.means.numpy())
    overlapping = distances < threshold
    
    if mode == 'weighted':
        for i, (dist, idx) in enumerate(zip(distances, indices)):
            if dist < threshold:
                w1, w2 = gs1.opacities[idx], gs2.opacities[i]
                merged.means[idx] = (w1 * gs1.means[idx] + w2 * gs2.means[i]) / (w1 + w2)
    # Add non-overlapping from gs2
    add_gaussians(merged, gs2, mask=~overlapping)
```

**Method 3: Joint optimization** on all source data after merge

**Method 4: Hierarchical merging** for large numbers of reconstructions""",
        "rejected": "Align the reconstructions using ICP, then merge the Gaussians with deduplication in overlapping regions. Optionally refine jointly."
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I integrate IMU data to improve 3DGS camera pose estimation?",
        "chosen": """**IMU integration for 3DGS:**

**IMU provides:** Angular velocity (gyroscope), linear acceleration (accelerometer)

**Benefits:** Better pose initialization, reduced drift, handle motion blur

**IMU preintegration:**
```python
class IMUPreintegrator:
    def __init__(self):
        self.delta_R = np.eye(3)
        self.delta_v = np.zeros(3)
        self.delta_p = np.zeros(3)
    
    def integrate(self, gyro, accel, dt):
        # Integrate rotation
        self.delta_R = self.delta_R @ so3_exp(gyro * dt)
        # Integrate velocity
        self.delta_v += self.delta_R @ accel * dt
        # Integrate position
        self.delta_p += self.delta_v * dt + 0.5 * self.delta_R @ accel * dt**2
```

**COLMAP with IMU priors:**
```python
def run_colmap_with_imu(images, imu_data):
    for i in range(1, len(images)):
        preint = preintegrate_imu(imu_data[i-1:i])
        relative_pose = compute_relative_pose(preint)
        database.set_pose_prior(i, relative_pose)
    return pycolmap.incremental_mapping(database_path, image_path, output_path)
```

**Factor graph optimization:**
```python
graph.add(gtsam.ImuFactor(
    gtsam.symbol('x', i-1), gtsam.symbol('v', i-1),
    gtsam.symbol('x', i), gtsam.symbol('v', i),
    gtsam.symbol('b', i), preintegrated_imu))
```

**Benefits for 3DGS:**
- More accurate camera poses → better reconstruction
- Handles fast motion (sports, UAV)
- Provides metric scale when combined with accelerometer""",
        "rejected": "Preintegrate IMU measurements between frames and use as relative pose priors in COLMAP or factor graph optimization."
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I create a unified coordinate frame for multi-sensor 3DGS?",
        "chosen": """**Unified coordinate frame for multi-sensor fusion:**

**Approach:** Define master frame, transform all sensors to it

**Coordinate frame convention:**
```
Master Frame (typically main camera or vehicle body):
  X: Forward
  Y: Left
  Z: Up (or Down, document clearly)
```

**Sensor-to-master transforms:**
```python
class MultiSensorRig:
    def __init__(self):
        self.transforms = {}  # sensor_name -> 4x4 matrix
        
    def add_sensor(self, name, R, t):
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t
        self.transforms[name] = T
    
    def sensor_to_master(self, sensor_name, points):
        T = self.transforms[sensor_name]
        points_h = np.hstack([points, np.ones((len(points), 1))])
        return (T @ points_h.T).T[:, :3]
    
    def master_to_world(self, master_pose, points):
        return (master_pose @ np.hstack([points, np.ones((len(points), 1))]).T).T[:, :3]
```

**Calibration workflow:**
1. Define master frame (e.g., left camera)
2. Calibrate each sensor to master (checkerboard, CAD, or optimization)
3. Store transforms in config file
4. Apply during data ingestion

**For 3DGS fusion:**
```python
def fuse_multimodal_3dgs(rgb_images, lidar_points, rig):
    # Transform LiDAR to camera frame
    lidar_in_camera = rig.sensor_to_master('lidar', lidar_points)
    
    # Run COLMAP on RGB
    colmap_output = run_colmap(rgb_images)
    
    # Initialize from fused point cloud
    combined_points = np.vstack([colmap_output.points3D, lidar_in_camera])
    gaussians = init_gaussians(combined_points)
    
    # Train with both RGB and depth supervision
    return train_3dgs_multimodal(gaussians, rgb_images, lidar_depth_maps)
```

**Validation:** Project known 3D points to all sensors, check alignment""",
        "rejected": "Define a master coordinate frame, calibrate all sensors relative to it, and transform all data to the master frame before fusion."
    },
]

