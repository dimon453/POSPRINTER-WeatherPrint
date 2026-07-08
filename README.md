# ☀ Weather Receipt Printer

Print beautiful weather information receipts on a thermal POS printer with a web-based control interface.

## Features

✨ **Core Features**
- 🌤️ Real-time weather data from OpenWeatherMap API
- 🖨️ Direct printing to thermal POS printers via Windows
- 🎛️ Web interface for easy management
- 📅 Scheduled automatic printing
- 🎨 Dynamic receipt width (16-80 characters)
- ❄️ ASCII weather icons
- 🌍 Multi-language city support
- 💾 Persistent configuration storage

✅ **Architecture**
- Dual-process design: Web GUI + Background service
- Independent operation (GUI can close, printing continues)
- REST API communication between components
- No external dependencies for printing

## System Requirements

- **OS**: Windows 7+
- **Python**: 3.8+
- **Printer**: Thermal POS printer (80mm recommended) connected via USB or network (POS895UE in my case)
- **Internet**: For OpenWeatherMap API access

## Installation

### 1. Install Python

Download from [python.org](https://python.org/downloads)

### 2. Clone/Download Project

```bash
git clone https://github.com/dimon453/POS895UE-WeatherPrint
cd POS895UE-WeatherPrint
```

Or download ZIP and extract.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get OpenWeatherMap API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up (free account)
3. Go to API keys section
4. Copy your default key

### 5. Verify Printer

1. Check Windows Settings → Devices → Printers
2. Your printer should be listed (e.g., "80mm Series Printer")
3. Test print from Notepad to verify it works

## Usage

### Quick Start

```bash
# Start the application
python weather_printer_app.py
```

Then open browser: **http://localhost:5000**

### First-Time Setup

1. **Paste API Key**
   - Get from OpenWeatherMap dashboard
   - Paste in "OpenWeatherMap API Key" field

2. **Select City**
   - Example: `Chisinau`, `New York`, `London`
   - Use English city names

3. **Select Printer**
   - Click "Refresh" button
   - Choose your printer from dropdown

4. **Configure Receipt**
   - **Tape Width**: Physical width of your printer (usually 80mm)
   - **Receipt Width**: Characters per line (16-80)
     - 24: Narrow receipts, fits most printers
     - 32: Medium receipts
     - 48+: Wide receipts for larger displays

5. **Save & Start**
   - Click "Save & Start" button
   - Service will start in background

### Test Print

Click **"🖨 Print Now"** button. Receipt should print within 2 seconds.

### Enable Scheduling

1. Check "Enable auto print"
2. Set print time (e.g., 09:00)
3. Select days of week (Mon-Sun)
4. Save configuration

Receipt will print automatically every selected day at that time.

## Configuration

### config.json

Auto-created after first save. Manual editing supported:

```json
{
    "openweather_api_key": "your_api_key_here",
    "city": "Chisinau",
    "printer_name": "80mm Series Printer",
    "tape_width_mm": 80,
    "receipt_width_chars": 24,
    "schedule": {
        "enabled": true,
        "time": "09:00",
        "days": ["MON", "TUE", "WED", "THU", "FRI"]
    }
}
```

**Fields:**
- `openweather_api_key`: API key from OpenWeatherMap
- `city`: City name (English, case-sensitive)
- `printer_name`: Exact printer name from Windows
- `tape_width_mm`: Physical printer width (32/60/80mm)
- `receipt_width_chars`: Characters per receipt line (16-80)
- `schedule.enabled`: Auto-print on/off
- `schedule.time`: Print time in HH:MM format
- `schedule.days`: Days to print (MON-SUN)



## Project Structure
weather-receipt-printer/
├── weather_printer_app.py      # Web GUI (Flask)
├── weather_bot.py              # Background service
├── weather_service.py          # OpenWeatherMap API
├── receipt_formatter.py        # Receipt formatting
├── printer_service.py          # Windows printing
├── requirements.txt            # Python dependencies
├── config.json                 # Configuration (auto-created)
└── README.md                   # This file

### File Descriptions

| File | Purpose |
|------|---------|
| `weather_printer_app.py` | Web interface on http://localhost:5000 |
| `weather_bot.py` | Background service (REST API on port 5001) |
| `weather_service.py` | Fetches weather from OpenWeatherMap |
| `receipt_formatter.py` | Formats weather data into receipt text |
| `printer_service.py` | Sends text to Windows printer via Notepad |

## Troubleshooting

### Printer not found in list

**Solution:**
1. Verify printer is on and connected
2. Check Windows Settings → Printers
3. Click "Refresh" button in web interface
4. Restart application if still missing

### API key error

**Solution:**
1. Check key for typos
2. Verify API is enabled in OpenWeatherMap dashboard
3. Wait 5 minutes after creating key (propagation delay)

### City not found

**Solution:**
1. Use English spelling: `Chisinau` not `Chișinău`
2. Try full name with country: `Chisinau, MD`
3. Check OpenWeatherMap for exact spelling

### Print appears but doesn't print

**Solution:**
1. Check printer is turned on
2. Verify it's set as default printer
3. Try manual test print from Notepad
4. Restart Windows Print Spooler:
```powershell
   net stop spooler
   net start spooler
```

### Nothing happens when clicking "Print Now"

**Solution:**
1. Check if service is running (green "RUNNING ✓" indicator)
2. Check browser console (F12) for errors
3. Restart application:
```bash
   # Press Ctrl+C to stop
   python weather_printer_app.py
```

### Receipt width doesn't match setting

**Solution:**
1. Verify `receipt_width_chars` in config.json matches web setting
2. Restart application to reload config
3. Check printer drivers aren't adding extra margins

## Advanced Usage

### Change Receipt Format

Edit `receipt_formatter.py` to customize layout, add/remove fields, change text alignment.

### Use Different Weather Source

Replace `weather_service.py` with your API provider while keeping same return format.

### Network Printer Support

Change `printer_service.py` to use network printing if printer supports IPP/LPR protocol.

### Docker Deployment

Create Dockerfile for containerized deployment (not included, requires Windows base image).

## API Endpoints (Background Service)

The background service runs on `http://localhost:5001`
POST /print-now          # Print weather immediately
GET /health              # Check service status

## Performance

- **Startup**: ~2 seconds
- **Print**: ~1-2 seconds
- **Weather fetch**: ~2-3 seconds (depends on internet)
- **Memory usage**: ~50-100 MB

## Known Limitations

- Windows only (uses Windows Print API and Notepad)
- Single printer at a time
- Printer must be installed in Windows Settings
- Internet required for weather data
- Background service runs continuously when enabled

## Future Enhancements

- [ ] Multiple printer support
- [ ] Cloud configuration storage
- [ ] Mobile app control
- [ ] Weather alerts/notifications
- [ ] Historical data tracking
- [ ] Custom receipt templates
- [ ] Linux/macOS support

## Security Notes

- API keys stored locally in config.json (not encrypted)
- Web interface runs on localhost only (no network access)
- No data sent to external services except OpenWeatherMap

For production use, consider:
- Using environment variables for API keys
- Adding HTTPS/authentication
- Running behind reverse proxy

## Contributing

Contributions welcome! Fork, modify, and submit pull requests.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check Troubleshooting section above
2. Review config.json settings
3. Check browser console for errors (F12)
4. Restart application and test again

## Credits

- Weather data: [OpenWeatherMap](https://openweathermap.org)
- Printing: Windows Print API via Notepad
- Framework: Flask

## Changelog

### v1.0.0 (2026-07-08)
- Initial release
- Web interface with full configuration
- Dynamic receipt width (16-80 characters)
- Scheduled printing support
- ASCII weather icons
- Thermal printer support via Windows

