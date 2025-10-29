param(
  [string]$Workspace='truck-rakshak',
  [string]$Project='fire-detection-k1ima',
  [int]$Limit=2000,
  [string]$SubsetOut='data/fire_yolo_2000'
)
$ErrorActionPreference='Stop'
function Get-PythonExe{if(Get-Command python -ErrorAction SilentlyContinue){return 'python'}elseif(Get-Command py -ErrorAction SilentlyContinue){return 'py'}else{throw 'Python not found. Install Python 3 first.'}}
$py=Get-PythonExe
if(-not $env:ROBOFLOW_API_KEY){
  throw 'Set ROBOFLOW_API_KEY environment variable with your Roboflow API key'
}
# install roboflow only if missing
try { & $py -c "import roboflow" | Out-Null } catch { & $py -m pip install roboflow }
& $py scripts/download_roboflow.py --workspace $Workspace --project $Project --limit $Limit --subset_out $SubsetOut
