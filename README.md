# Aircraft Tracker

A simple desktop application that shows a live, updating map of aircraft within a radius of the user's current location.

## Setup

Linux / macOS

```bash
cd aircraft_tracker
./setup/setup.sh
```

Windows (PowerShell)

```powershell
cd aircraft_tracker
.\setup\setup.ps1
```

## Configuration

- Default radius: 50 km
- Default refresh interval: 30 seconds

You can change these in `main.py` or pass environment variables (TBD).

## Troubleshooting

- If the OpenSky API is unreachable, check your network and try again.
- If geolocation fails, the app falls back to a default location (TBD).

## License

MIT
