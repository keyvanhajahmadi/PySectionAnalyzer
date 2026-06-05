# structural-section-centroid
Python tool for calculating the centroid of composite sections used in civil and structural engineering.
# 🏗️ Structural Section Centroid Calculator

![Structural Engineering Banner](./banner.png)

## 📌 Project Overview
This Python-based engineering tool is designed to calculate the **Centroid (X̄, Ȳ)** of composite structural sections. Understanding the centroidal axis is fundamental for calculating the Moment of Inertia, Section Modulus, and overall structural stability in civil engineering design.

This project was developed during my undergraduate studies at **Shahid Bahonar University of Kerman** to bridge the gap between theoretical structural mechanics and computational engineering.

---

## 🚀 Key Features
- **Multi-Shape Support:** Handles Rectangles, Triangles, and Circles.
- **Composite Analysis:** Supports addition and subtraction (holes/cutouts) of areas.
- **Precision:** High-accuracy coordinate calculation for complex geometries.
- **Clean Architecture:** Built using modular Python functions for easy scalability.

---

## 🛠️ Mathematical Background
The program utilizes the first moment of area principle:

$$ \bar{X} = \frac{\sum (A_i \cdot x_i)}{\sum A_i} $$
$$ \bar{Y} = \frac{\sum (A_i \cdot y_i)}{\sum A_i} $$

Where $A_i$ is the area of each individual shape and $(x_i, y_i)$ are the coordinates of their respective centroids.

---

## 💻 Installation & Usage

1. **Clone the repository:**
```bash
   git clone https://github.com/keyvanhajahmadi/structural-section-centroid.git
   
## 📖 How to Use
After running `main.py`, follow the prompts:
1. Enter the number of sub-shapes in your composite section.
2. For each shape, provide:
   - **Type:** (e.g., Rectangle, Circle)
   - **Dimensions:** (Width, Height or Radius)
   - **Coordinates:** (x, y) of the shape's own centroid.
3. The program will automatically compute the global centroid.
