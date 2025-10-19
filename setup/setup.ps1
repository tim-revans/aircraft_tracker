Write-Host "🔧 Setting up virtual environment..."
if (!(Test-Path "venv")) {
    python -m venv venv
}
Write-Host "📦 Activating environment and installing dependencies..."
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host "🚀 Launching app..."
python main.py
