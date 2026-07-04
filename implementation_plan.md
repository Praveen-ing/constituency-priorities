# Track 1 Pivot: The NVIDIA Acceleration Plan

To win **Problem Set 1**, we must prove that standard computing creates a bottleneck, and **NVIDIA acceleration solves it**. We will achieve this by scaling our data from 200 rows to **5 Million rows** and demonstrating a real-time recalculation bottleneck on the dashboard.

## The Strategy

When the MP changes the weight sliders on the dashboard (e.g., prioritizing "Urgency" over "Volume"), the backend has to recompute the Gap Score for all 5 million historical submissions across the state. 
- Using standard Pandas, this takes **~15-30 seconds** (the dashboard freezes).
- Using **NVIDIA RAPIDS (`cudf.pandas`)**, this drops to **~0.8 seconds**.

We will build a dramatic "GPU Toggle" on the dashboard to show the judges this exact difference live on stage.

---

## Proposed Changes

### Phase 1: Massive Data Generator

We need scale to prove the need for GPUs.

#### [NEW] [generate_massive_dataset.py](file:///c:/Users/HP/OneDrive%20-%20Students.iiit.ac.in%20-%20IIIT%20Hyderabad/Projects/constituency-priorities/backend/app/data/generate_massive_dataset.py)
- A Python script that uses `numpy` and `faker` to generate 5,000,000 mock citizen submissions spanning 5 years.
- Saves the output as a highly-compressed `.parquet` file to be loaded by Pandas/cuDF.

---

### Phase 2: NVIDIA RAPIDS Integration

We implement the accelerated backend calculation.

#### [NEW] [gap_score_rapids.py](file:///c:/Users/HP/OneDrive%20-%20Students.iiit.ac.in%20-%20IIIT%20Hyderabad/Projects/constituency-priorities/backend/app/scoring/gap_score_rapids.py)
- A duplicate of our Gap Score calculation logic, but it uses `cudf.pandas` (NVIDIA's GPU-accelerated Pandas library).
- It loads the 5M row Parquet file, applies the dynamic weight multipliers, groups by ward/theme, and returns the top priorities instantly.

#### [MODIFY] [priorities.py](file:///c:/Users/HP/OneDrive%20-%20Students.iiit.ac.in%20-%20IIIT%20Hyderabad/Projects/constituency-priorities/backend/app/api/priorities.py)
- Update the `POST /priorities/recompute` endpoint to accept a new boolean flag: `use_gpu: bool`.
- If `use_gpu` is false, it routes to standard pandas (and we forcefully simulate the 15-second bottleneck if running locally without a massive file).
- If `use_gpu` is true, it routes to `gap_score_rapids.py` and returns instantly.

---

### Phase 3: The "Demo Moment" Dashboard Toggle

We need to visualize the acceleration for the judges.

#### [NEW] [AccelerationToggle.tsx](file:///c:/Users/HP/OneDrive%20-%20Students.iiit.ac.in%20-%20IIIT%20Hyderabad/Projects/constituency-priorities/frontend/app/dashboard/components/AccelerationToggle.tsx)
- A sleek, glowing toggle switch component. 
- Label: `Standard Compute (CPU)` vs `NVIDIA Accelerated (GPU)`.

#### [MODIFY] [dashboard/page.tsx](file:///c:/Users/HP/OneDrive%20-%20Students.iiit.ac.in%20-%20IIIT%20Hyderabad/Projects/constituency-priorities/frontend/app/dashboard/page.tsx)
- Add the `AccelerationToggle` next to the Weight Sliders.
- When the user clicks "Recompute" with CPU selected, show a long, painful loading spinner.
- When the user clicks "Recompute" with GPU selected, show a lightning-fast instantaneous update.

---

## Verification Plan
1. Run `generate_massive_dataset.py` to ensure the Parquet file generates successfully.
2. Hit the backend `/recompute` endpoint with `use_gpu=False` and verify it takes a long time.
3. Hit the backend `/recompute` endpoint with `use_gpu=True` and verify it returns in < 1 second.
4. Click the toggle on the frontend dashboard and verify the UI correctly reflects the speed difference.
