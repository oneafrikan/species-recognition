# Wildlife Vision Models: Complete Implementation & Test Registry

This document serves as a comprehensive registry of vision models suitable for wildlife photography tagging, structured for direct parsing by an AI coding or automation agent.

---

## 1. Specialized Biodiversity & Filtering Models

### MegaDetector (v5 / v6)
* **Hugging Face / Repository ID:** `microsoft/CameraTraps` (or `agent-search: MegaDetector v5/v6 github`)
* **Primary Category:** Object Detection & Frame Filtering
* **Output Classes:** `[Animal, Human, Vehicle, Empty]`
* **Implementation Context:** 
  * Use as a **Stage 1 pipeline step** to drop empty background frames before passing cropped regions to a species classifier.
  * Model architectures typically utilize YOLOv5/YOLOv8 backbones customized for camera traps.

### BioCLIP
* **Hugging Face / Repository ID:** `imageomics/bioclip`
* **Primary Category:** Zero-Shot Taxonomic Classification
* **Output Classes:** Broad biodiversity taxonomy (Plants, Animals, Fungi, Insects).
* **Implementation Context:**
  * Tree of Life foundation model based on open-source CLIP architecture.
  * Excellent for zero-shot text-to-image taxonomic labeling using scientific or common names.

### SpeciesNet
* **Hugging Face / Repository ID:** `google/speciesnet` (or `agent-search: SpeciesNet open-source classifier`)
* **Primary Category:** Global Species Classification
* **Output Classes:** ~2,500 distinct wildlife species.
* **Implementation Context:**
  * Pre-trained out-of-the-box global model specifically built to reduce labeling friction for ecological organizations.

### SA-FARI (SAM3 for Wildlife)
* **Hugging Face / Repository ID:** `agent-search: SA-FARI wildlife segmentation tracking`
* **Primary Category:** Semantic Segmentation & Behavioral Tracking
* **Output Classes:** Custom fine-tuned bounding polygons & instance tracking masks.
* **Implementation Context:**
  * Utilizes Segment Anything Model (SAM) layers specialized for tracking movement and tracking boundaries across complex foliage backgrounds.

---

## 2. General-Purpose Vision Transformers & Object Detection

### DINOv2
* **Hugging Face / Repository ID:** `facebook/dinov2-base` or `facebook/dinov2-large`
* **Primary Category:** Self-Supervised Vision Transformer (Feature Extractor)
* **Output Classes:** Embeddings / Custom downstream classification layer.
* **Implementation Context:**
  * Highly robust visual representation model. Use it to extract feature embeddings from your wildlife photos and train a simple downstream classifier (like a linear probe or SVM) if your target species are highly specific.

### BLIP / BLIP-2
* **Hugging Face / Repository ID:** `Salesforce/blip-image-captioning-large` or `Salesforce/blip2-opt-2.7b`
* **Primary Category:** Vision-Language Model (Captioning & Tagging)
* **Output Classes:** Free-text descriptions / Attribute lists.
* **Implementation Context:**
  * Ideal for generating rich visual tags such as lighting, weather, behavior, and physical actions ("swimming", "climbing").

### PaliGemma 2
* **Hugging Face / Repository ID:** `google/paligemma2-3b-pt-448`
* **Primary Category:** Lightweight Vision-Language Model
* **Output Classes:** Dense captioning, visual question answering, structured json object detection.
* **Implementation Context:**
  * Highly efficient open-weights VLM suitable for low-latency zero-shot edge processing or local deployment.

### YOLOv8 / YOLOv10 / YOLOv11
* **Hugging Face / Repository ID:** `ultralytics/yolov8n` or `ultralytics/yolov10n`
* **Primary Category:** Real-Time Custom Object Detection
* **Output Classes:** Requires a user-provided labeled dataset (e.g., via Roboflow).
* **Implementation Context:**
  * Unrivaled for speed and local hardware efficiency. Instruct your agent to configure a script using the `ultralytics` package for transfer learning on localized regional species.

---

## 3. Commercial & Frontier APIs (For Complex Contextual Tagging)

### GPT-4o
* **API Endpoint / Model Identifier:** `gpt-4o` or `gpt-4o-mini`
* **Primary Category:** Multi-Modal Frontier Foundation Model
* **Output Classes:** Highly detailed structured JSON strings containing species, count, background descriptions, and behavior metrics.
* **Implementation Context:**
  * High-cost option best utilized for deep behavioral analytics or complex reasoning queries ("Describe the health state of the animal").

### Claude 3.5 Sonnet
* **API Endpoint / Model Identifier:** `claude-3-5-sonnet-latest`
* **Primary Category:** Multi-Modal Frontier Foundation Model
* **Output Classes:** High-fidelity markdown descriptions or structured configuration tags.
* **Implementation Context:**
  * Renamed for exceptional accuracy in recognizing precise object details and following strict structured response schema formatting.

---

## 4. Multi-Stage Pipeline Evaluation Blueprint

Your AI agent can orchestrate the testing environment following this workflow logic:

```
[Raw Photo Dataset]
       │
       ▼
 ┌───────────┐
 │ Stage 1   │ ──(If Category == 'Empty')──> [Discard / Archive Archive File]
 │ (Filter)  │
 └───────────┘
   │ (If Category == 'Animal')
   ▼
 ┌───────────┐
 │ Cropper   │ ──> [Generates cropped animal frame bounding boxes]
 └───────────┘
   │
   ▼
 ┌───────────┐
 │ Stage 2   │ ──> [Taxonomic / Species Labeling] -> (BioCLIP, SpeciesNet, YOLO)
 │ (Classify)│
 └───────────┘
   │
   ▼
 ┌───────────┐
 │ Stage 3   │ ──> [Contextual & Behavioral Annotation] -> (BLIP-2, PaliGemma 2, GPT-4o)
 │ (Context) │
 └───────────┘
```
