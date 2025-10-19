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

## Continuous Integration (CI)

When running tests in headless CI (GitHub Actions on Ubuntu) the Qt GUI libraries
and Qt WebEngine can crash if no display is available or the WebEngine sandbox
is enabled. The CI workflow sets the following to avoid aborts during tests:

- Run pytest under Xvfb (provides a virtual display)
- Set `QT_QPA_PLATFORM=offscreen`
- Set `QTWEBENGINE_DISABLE_SANDBOX=1`

These are applied in `.github/workflows/ci.yml`.

You can also force-disable WebEngine when running tests locally by setting
`AIRCRAFT_TRACKER_DISABLE_WEBENGINE=1`. This makes the application create a
lightweight placeholder for the map view which avoids starting Qt WebEngine
processes (useful for headless/local testing).

## License

MIT
