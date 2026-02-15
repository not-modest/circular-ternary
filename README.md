# 🔄 Circular Economy Assessment - Streamlit GUI

Interactive web application for circular economy lifecycle assessment using 3D ternary burden-space visualization.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [File Structure](#file-structure)
4. [How to Run](#how-to-run)
5. [Using the Application](#using-the-application)
6. [Tunable Parameters](#tunable-parameters)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

You need Python 3.8+ installed on your system.

### Installation (3 steps)

```bash
# Step 1: Install required packages
pip install streamlit plotly numpy pandas

# Step 2: Navigate to your project directory
cd path/to/your/project

# Step 3: Run the app
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`

---

## 📦 Installation (Detailed)

### Option 1: Using pip (Recommended)

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install streamlit==1.31.0
pip install plotly==5.18.0
pip install numpy==1.24.3
pip install pandas==2.0.3
```

### Option 2: Using requirements.txt

Create a file named `requirements.txt` with:

```txt
streamlit==1.31.0
plotly==5.18.0
numpy==1.24.3
pandas==2.0.3
```

Then run:

```bash
pip install -r requirements.txt
```

### Option 3: Using conda

```bash
conda create -n circular_economy python=3.11
conda activate circular_economy
pip install streamlit plotly numpy pandas
```

---

## 📁 File Structure

Your project directory should contain these files:

```
your_project/
│
├── app.py                    # Main Streamlit application
├── circularity_core.py       # Core calculation engine
├── README.md                 # This file
└── requirements.txt          # (Optional) Package dependencies
```

**Important:** Both `app.py` and `circularity_core.py` must be in the same directory!

---

## ▶️ How to Run

### Step-by-Step Instructions

#### Step 1: Open Terminal/Command Prompt

- **Windows:** Press `Win + R`, type `cmd`, press Enter
- **macOS:** Press `Cmd + Space`, type `Terminal`, press Enter  
- **Linux:** Press `Ctrl + Alt + T`

#### Step 2: Navigate to Your Project Directory

```bash
# Replace with your actual path
cd C:\Users\YourName\Documents\circular_economy
# or on macOS/Linux:
cd ~/Documents/circular_economy
```

#### Step 3: Verify Files Exist

```bash
# On Windows:
dir

# On macOS/Linux:
ls
```

You should see:
- `app.py`
- `circularity_core.py`

#### Step 4: Run Streamlit

```bash
streamlit run app.py
```

#### Step 5: Access the Application

- Your default browser will open automatically
- If not, manually navigate to: **http://localhost:8501**
- To stop the app: Press `Ctrl + C` in the terminal

---

## 🎯 Using the Application

### Interface Overview

The application has 4 main sections:

1. **Sidebar (Left):** Global settings and pathway selection
2. **Main Tabs:** Individual pathway configuration
3. **Visualization:** Interactive 3D plot
4. **Summary Table:** Comparison metrics

### Workflow

#### 1. Configure Global Settings (Sidebar)

**Benchmarks:**
- **Cost Max:** Maximum cost for normalization (default: $7/kg)
- **Environmental Max:** Maximum CO₂ emissions (default: 10 kg CO₂-eq/kg)

**Constraints (Optional):**
- Toggle "Enable Constraints" to set feasibility limits
- Set maximum acceptable values for cost, environmental impact, and minimum integrity

**Pathway Selection:**
- Check/uncheck pathways to include in analysis:
  - ✅ Mechanical Recycling
  - ✅ Chemical Recycling  
  - ✅ Downcycling

#### 2. Configure Pathways (Tabs)

Navigate through tabs to configure each pathway:

**Tab 1: ⚙️ Mechanical Recycling**
- Virgin production parameters
- Bottle use parameters
- Recycling loop parameters (with per-cycle degradation)

**Tab 2: 🧪 Chemical Recycling**
- Advanced recycling with lower degradation
- Higher cost but maintains quality

**Tab 3: 📦 Downcycling**
- Single-cycle cascade to carpet fiber
- Terminal application (exits closed-loop)

**Tab 4: 📊 Visualization Settings**
- Toggle triangle frames, constraints, labels
- Adjust camera position (X, Y, Z)

#### 3. View Results

Results update automatically when parameters change:

- **3D Visualization:** Interactive ternary burden-space plot
  - Rotate: Click + drag
  - Zoom: Scroll wheel
  - Pan: Shift + drag
  - Hover: See detailed metrics

- **Summary Table:** Quantitative comparison of pathways
  - Total costs, environmental impact, integrity loss
  - Rates per year

- **Export:** Download results as CSV

---

## 🎛️ Tunable Parameters (74 Total!)

### Global Parameters (5)

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| Cost Max | Normalization benchmark | 1-20 $/kg | 7.0 |
| Environmental Max | Normalization benchmark | 1-50 kg CO₂ | 10.0 |
| Max Acceptable Cost | Constraint (optional) | 0-10 $/kg | 5.0 |
| Max Acceptable Environmental | Constraint (optional) | 0-20 kg CO₂ | 8.0 |
| Min Integrity | Constraint (optional) | 0-100% | 15% |

### Per-Pathway Parameters (21 each)

Each pathway has 3 stages × 7 parameters = 21 parameters:

#### Virgin Production Stage
1. Cost ($/kg)
2. Environmental (kg CO₂-eq/kg)
3. Integrity Loss (0-1)
4. Duration (years)
5. Mass Fraction (0-1)

#### Use Stage (Bottle)
6. Cost ($/kg)
7. Environmental (kg CO₂-eq/kg)
8. Integrity Loss (0-1)
9. Duration (years)
10. Mass Fraction (0-1)

#### Recycling Stage
11. Base Cost ($/kg)
12. Base Environmental (kg CO₂-eq/kg)
13. Base Integrity Loss (0-1)
14. Duration per Cycle (years)
15. Mass Fraction per Cycle (0-1)
16. **Number of Cycles** (1-50)
17. **Cost Increase per Cycle** ($/kg)
18. **Environmental Increase per Cycle** (kg CO₂)
19. **Integrity Increase per Cycle** (0-1)

### Visualization Parameters (6)

20. Show Triangle Frames (toggle)
21. Show Constraint Boundaries (toggle)
22. Show Axis Labels (toggle)
23. Camera X position (0-3)
24. Camera Y position (0-3)
25. Camera Z position (0-2)

### Total: **74 tunable parameters** across all pathways!

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
pip install streamlit plotly numpy pandas
```

### Issue: "ModuleNotFoundError: No module named 'circularity_core'"

**Solution:**
- Ensure `circularity_core.py` is in the same directory as `app.py`
- Run `streamlit run app.py` from the directory containing both files

### Issue: Browser doesn't open automatically

**Solution:**
- Manually open: http://localhost:8501
- Check terminal for alternative URL (e.g., http://192.168.1.X:8501)

### Issue: "Port 8501 is already in use"

**Solution:**
```bash
# Kill existing Streamlit process
# On Windows:
taskkill /F /IM streamlit.exe

# On macOS/Linux:
pkill -f streamlit

# Or use a different port:
streamlit run app.py --server.port 8502
```

### Issue: Plot not displaying

**Solution:**
- Ensure at least one pathway is enabled in sidebar
- Check browser console for JavaScript errors (F12)
- Try refreshing the page (F5)

### Issue: Slow performance with many cycles

**Solution:**
- Reduce "Number of Cycles" to <30
- Disable "Show Triangle Frames" for faster rendering

### Issue: Parameters not updating

**Solution:**
- Click outside the input box to apply changes
- Press Enter after typing values
- Check for validation errors (red text)

---

## 📚 Additional Features

### Keyboard Shortcuts

- **R:** Refresh app
- **C:** Clear cache
- **Esc:** Close sidebar (if open)

### Advanced Usage

#### Running on a Different Port

```bash
streamlit run app.py --server.port 8502
```

#### Running on Network (Access from other devices)

```bash
streamlit run app.py --server.address 0.0.0.0
```

Then access from other devices using: `http://YOUR_IP:8501`

#### Running in Dark Mode

Add to `~/.streamlit/config.toml`:

```toml
[theme]
base="dark"
```

---

## 🎓 Understanding the Visualization

### 3D Ternary Burden-Space

The visualization shows material lifecycle trajectories in a 3D space:

- **X-Y Plane:** Ternary diagram representing burden composition
  - Cost burden (left vertex)
  - Environmental burden (right vertex)
  - Integrity loss (top vertex)

- **Z-Axis:** Time (cumulative years)

- **Triangle Size:** Represents absolute burden magnitude
  - Larger triangles = higher total burden
  - Triangles shrink as burdens decrease

- **Color-Coded Edges:**
  - 🔵 Blue: Cost edge
  - 🟢 Green: Environmental edge
  - 🟠 Orange: Integrity loss edge

- **Trajectory Points:**
  - Color intensity = total burden
  - Hover for detailed metrics

### Interpreting Results

**Good Pathway Characteristics:**
- Smaller triangles (lower absolute burden)
- Points near origin (low total burden)
- Green markers (low burden magnitude)
- Many cycles before quality degrades

**Poor Pathway Characteristics:**
- Large triangles (high absolute burden)
- Points far from origin
- Red markers (high burden magnitude)
- Few cycles (rapid quality degradation)

---

## 📖 Example Use Cases

### 1. Comparing Recycling Technologies

**Scenario:** Compare mechanical vs. chemical recycling

**Steps:**
1. Enable both pathways in sidebar
2. Adjust degradation rates:
   - Mechanical: Higher integrity loss per cycle (0.06)
   - Chemical: Lower integrity loss per cycle (0.012)
3. Observe:
   - Chemical allows more cycles but costs more
   - Mechanical is cheaper but degrades faster

### 2. Optimizing for Cost

**Scenario:** Find lowest-cost pathway under $5/kg constraint

**Steps:**
1. Enable constraints in sidebar
2. Set "Max Acceptable Cost" to $5.00
3. Adjust pathway costs to stay under limit
4. Compare final costs in summary table

### 3. Environmental Impact Analysis

**Scenario:** Minimize carbon footprint

**Steps:**
1. Focus on "Environmental" parameters
2. Lower environmental values for each stage
3. Increase cycles to extend material lifespan
4. Check "Total Env" column in summary

---

## 🆘 Getting Help

### Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Plotly Docs:** https://plotly.com/python/
- **Python Docs:** https://docs.python.org/3/

### Common Questions

**Q: How many pathways can I compare?**  
A: Up to 3 simultaneously (Mechanical, Chemical, Downcycling)

**Q: Can I add custom pathways?**  
A: Yes! Edit `app.py` to add new pathway configurations

**Q: Can I export the 3D plot?**  
A: Yes! Click camera icon in top-right of plot → "Download plot as PNG"

**Q: What do the per-cycle increases represent?**  
A: They model degradation over repeated cycles (e.g., polymer chain scission, contamination buildup)

---

## 🏁 Summary

You now have a fully functional Streamlit GUI with:

✅ **74 tunable parameters**  
✅ **3 pre-configured circular economy pathways**  
✅ **Interactive 3D ternary visualization**  
✅ **Real-time parameter adjustment**  
✅ **Constraint validation**  
✅ **CSV export functionality**  
✅ **Responsive web interface**

**Happy exploring!** 🔄🌍

---

## 📝 Citation

If you use this tool in research, please cite:

```bibtex
@software{circular_economy_assessment,
  title={Circular Economy Lifecycle Assessment Tool},
  author={[Your Name]},
  year={2026},
  version={1.0}
}
```

---

**Version:** 1.0  
**Last Updated:** February 2026  
**License:** MIT
