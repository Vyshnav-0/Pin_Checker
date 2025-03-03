# Android PIN Checker (Professional Edition)

A professional tool for testing Android PIN combinations with a sleek interface and progress tracking.

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ⚠️ Disclaimer

This tool is for educational and testing purposes only. Use it only on devices you own or have explicit permission to test. Unauthorized access to devices is illegal.

## 🚀 Features

- Professional interface with progress tracking
- Smart screen size detection
- Automatic timeout handling
- Detailed progress and statistics
- Error handling and recovery
- Beautiful colored output
- Real-time progress bars
- Time elapsed tracking

## 📋 Prerequisites

1. Linux-based operating system (Ubuntu, Debian, Arch, Fedora)
2. Python 3.6 or higher
3. USB cable
4. Android device with USB debugging enabled

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/android-pin-checker
cd android-pin-checker
```

2. Install ADB (Android Debug Bridge):

For Ubuntu/Debian:
```bash
sudo apt update
sudo apt install adb
```

For Arch Linux:
```bash
sudo pacman -S android-tools
```

For Fedora:
```bash
sudo dnf install android-tools
```

3. Install Python dependencies:
```bash
python3 -m pip install rich
```

## 📱 Android Device Setup

1. Enable Developer Options:
   - Go to Settings > About phone
   - Find "Build number"
   - Tap "Build number" 7 times
   - You'll see a message that you're now a developer

2. Enable USB Debugging:
   - Go back to Settings
   - Go to System > Developer options
   - Enable "USB debugging"
   - Enable "Stay awake" (optional, but recommended)

3. Connect Your Device:
   - Connect your phone to computer via USB
   - Set USB mode to "File Transfer" (MTP)
   - Accept the "Allow USB debugging" prompt on your phone

## 🎯 Usage

1. Verify ADB Connection:
```bash
adb devices
```
You should see your device listed.

2. Run the PIN Checker:
```bash
python3 pin_checker.py
```

3. Follow the on-screen instructions:
   - The script will perform initial checks
   - Wait for the screen unlock sequence
   - The tool will start testing PINs
   - Progress will be shown in real-time

## 📊 Features Explained

- **Initial Unlock**: The tool performs one initial swipe to reach the PIN entry screen
- **Smart Timing**: Pauses for 30 seconds after every 5 attempts to prevent device lockout
- **Progress Tracking**: Shows:
  - Current PIN being tested
  - Percentage complete
  - Time elapsed
  - Total attempts made
- **Error Recovery**: Handles connection issues and input errors gracefully

## 🔍 Understanding the Output

The tool provides various visual indicators:

- 🔵 Blue text: Information and status messages
- 🟡 Yellow text: Warnings and important notices
- 🔴 Red text: Errors and failures
- 🟢 Green text: Success messages

Progress bar shows:
```
[••••••••••] Testing PIN: 1234 | 45% | Time: 00:15:30
```

## ⚡ Performance Tips

1. Keep your phone's screen on
2. Disable any screen lock timeout
3. Keep the USB connection stable
4. Don't touch the phone during testing
5. Ensure phone has sufficient battery (>20%)

## 🔒 Security Notes

- The tool pauses every 5 attempts to prevent device lockout
- Some devices may have additional security measures
- The tool respects device security timeouts
- Always monitor the process to prevent device locks

## 🛠️ Troubleshooting

1. **ADB not detecting device**:
   - Check USB cable
   - Reinstall ADB: `sudo apt install --reinstall android-tools-adb`
   - Try different USB ports
   - Restart ADB server:
     ```bash
     adb kill-server
     adb start-server
     ```

2. **Screen not unlocking**:
   - Check USB debugging is enabled
   - Accept USB debugging prompt on phone
   - Try different swipe coordinates
   - Increase swipe duration

3. **PIN entry not working**:
   - Check phone is awake
   - Verify ADB connection
   - Try manual PIN entry to verify screen state

## 📝 Logs

The tool maintains logs with timestamps:
```
[12:34:56] Device connected: SAMSUNG_A515F
[12:34:57] Screen size detected: 1080x2400
[12:34:58] Starting PIN sequence...
```

## ⚖️ Legal

This tool is provided for educational purposes only. Users are responsible for complying with local laws and regulations regarding device access and security testing.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 