# aca2040-90um_demo

This is a simple Python script to preview a live video stream from a Basler USB3 Vision camera.

## Requirements

- Python 3.8+
- Basler USB camera
- Pylon SDK (make sure it's in your system PATH)
- Modules listed in `requirements.txt`

## Quick Start

Follow these steps to get things running:

### 1. Clone the repository or download the ZIP

### 2. Create a virtual environment

```
python -m venv venv
```

### 3. Activate the virtual environment

#### On Windows:
```
venv\Scripts\activate
```

#### On Linux/macOS:
```
source venv/bin/activate
```

### 4. Install all required Python modules
```
pip install -r requirements.txt
```

### 5. Run the script
Make sure your Basler camera is connected, then run:

#### Basic camera test:
```
python camera_test.py
```

#### Camera test with a simple UI (adjustable Gain and FPS):
```
python camera_demo.py
```