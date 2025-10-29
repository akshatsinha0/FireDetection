# sets up project deps and verifies GPU torch
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$root\.."
function Get-PythonExe{if(Get-Command python -ErrorAction SilentlyContinue){return 'python'}elseif(Get-Command py -ErrorAction SilentlyContinue){return 'py'}else{throw 'Python not found. Install Python 3 first.'}}
$py=Get-PythonExe
# torch+cuda
& "$root\install_torch_gpu.ps1"
# libs
& $py -m pip install -r requirements.txt
# verify
& $py scripts/verify_gpu.py
Write-Host 'setup done'
