# Feedy

Frontend mobile-first interface for the automated pet feeder, designed for Raspberry Pi and Flask backend integration.

## Structure

- `app/`: Flask application
  - `static/css/`: styles
  - `static/js/`: frontend interactions
  - `static/images/`: local images and assets
  - `templates/`: UI templates
- `src/images/`: design references and source assets
- `run.py`: app entry point
- `requirements.txt`: Python dependencies

## Run locally

```bash
cd /home/valentin/Documents/Feedy
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

Then open:

- http://127.0.0.1:5000
- or http://<raspberry-pi-ip>:5000

## Included UI behaviors

- Mobile-first green themed layout based on the reference image
- Portion configuration modal with Save and Test Portion actions
- Live camera modal with close button
- Configured schedule table with two-step delete confirmation
- Device connection status indicator
