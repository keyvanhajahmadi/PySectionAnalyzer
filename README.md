# PyStruct Analyzer

![Banner](banner.png)

**PyStruct Analyzer** is a Python-based structural engineering toolkit designed to perform section property calculations and structural analysis within a simple graphical interface.

The goal of this project is to bridge classical structural engineering concepts with computational tools, allowing engineers and students to analyze structural components quickly and efficiently.

---

# Features

## Section Analysis
Calculate geometric properties of structural sections:

- Area
- Centroid (X̄ , Ȳ)
- Second Moment of Area (Ixx, Iyy)
- Polar Moment of Inertia
- Section Modulus
- Composite section support

Supports multiple shapes such as:

- Rectangle
- Triangle
- Circle

Composite sections can include both **added areas and holes**.

---

## Structural Analysis

### 2D Truss Solver

The truss module is based on the **Direct Stiffness Method**, widely used in structural engineering software.

Capabilities include:

- Global stiffness matrix assembly
- Node displacement calculation
- Support reaction calculation
- Member axial force calculation
- Tension / Compression detection

Mathematical formulation:

F = K × U

Where

- F = force vector
- K = global stiffness matrix
- U = displacement vector

---

# Graphical User Interface

The application includes a lightweight GUI built using **Tkinter**, enabling engineers to:

- Input geometry and structural parameters
- Perform calculations instantly
- View organized results

---

# Technology Stack

Python  
NumPy  
SciPy  
Tkinter

These libraries allow efficient matrix computations and numerical solving for structural systems.

---

# Installation

Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/PyStruct-Analyzer.git
