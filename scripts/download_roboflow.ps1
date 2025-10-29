param(
  [string]$Workspace='truck-rakshak',
  [string]$Project='fire-detection-k1ima',
  [int]$Limit=2000,
  [string]$SubsetOut='data/fire_yolo_2000'
)
$ErrorActionPreference='Stop'
function Get-PythonExe{if(Get-Command python -ErrorAction SilentlyContinue){return 'python'}elseif(Get-Command py -ErrorAction SilentlyContinue){return 'py'}else{throw 'Python not found. Install Python 3 first.'}}
function Load-DotEnv([string]$path='.env'){
  if(Test-Path $path){
    Get-Content $path | ForEach-Object {
      $line=$_.Trim(); if(-not $line -or $line.StartsWith('#')){return}
      $kv=$line -split '=',2; if($kv.Length -eq 2){$k=$kv[0].Trim(); $v=$kv[1].Trim(); if($k){ Set-Item -Path ("Env:"+$k) -Value $v -ErrorAction SilentlyContinue | Out-Null }}
    }
  }
}
$py=Get-PythonExe
# load .env if present (does not print secrets)
Load-DotEnv
if(-not $env:ROBOFLOW_API_KEY){
  throw 'ROBOFLOW_API_KEY not found. Add it to .env as ROBOFLOW_API_KEY=<your_key>'
}
# install roboflow only if missing
try { & $py -c "import roboflow" | Out-Null } catch { & $py -m pip install roboflow }
& $py scripts/download_roboflow.py --workspace $Workspace --project $Project --limit $Limit --subset_out $SubsetOut
