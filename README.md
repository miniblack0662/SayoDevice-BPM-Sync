# Features:

### ​1. Real-time BPM Synchronization
- Visualizes your tapping speed with RGB lighting


### ​2. Dynamic Key Binding
- Customize which keys to monitor (Key 1, 2, 3)
- ​Works with any keyboard input
(it monitors global system input rather than direct HID reports from the SayoDevice hardware)


### ​3. Color Picker
- Select your own start (idle) and end (peak) colors via a native color dialog


# Setup:

### 1. Clone this repository
```
git clone https://github.com/miniblack0662/SayoDevice-O3C-BPM-Sync
```
### 2. Install dependencies
```
pip install -r requirements.txt
```
### 3. Clone LiTLiTschi/sayodevice-o3c-fuckerr (one of the dependencies, it cannot be found on PyPl)
```
git clone https://github.com/LiTLiTschi/sayodevice-o3c-fuckerr
```
### 4. Install module "sayodevice" (from source)
```
cd path/to/sayodevice-o3c-fuckerr

pip install .
```


# Usage:
```
cd path/to/SayoDevice-O3C-BPM-Sync

python app.py
```

> [!IMPORTANT]
> If you have the SayoDevice Web Configurator (Official Website) or other third-party sync software open in your browser or background, this program will likely fail


# Showcase
[![YouTube](https://github.com/miniblack0662/SayoDevice-BPM-Sync/blob/main/images/thumbnail.jpg)](https://youtu.be/q6A8Z27x5aI?si=ZLEUqJu5vPDpDXdG)
[!image](https://github.com/miniblack0662/SayoDevice-BPM-Sync/blob/main/images/gui.png)
