# installs torch with CUDA matching your NVIDIA driver; reuses existing install if OK
$ErrorActionPreference='Stop'
function Get-PythonExe{if(Get-Command py -ErrorAction SilentlyContinue){return 'py -3'}elseif(Get-Command python -ErrorAction SilentlyContinue){return 'python'}else{throw 'Python not found. Install Python 3 first.'}}
function Get-CudaSlug{
  if(!(Get-Command nvidia-smi -ErrorAction SilentlyContinue)){Write-Warning 'nvidia-smi not found; installing CPU torch fallback';return $null}
  $out=(nvidia-smi) -join " `n"
  $m=[regex]::Match($out,'CUDA Version:\s*([0-9]+\.[0-9]+)')
  if(!$m.Success){Write-Warning 'CUDA version not detected; using CPU torch';return $null}
  $v=[double]$m.Groups[1].Value
  if($v -ge 12.6){return 'cu126'}elseif($v -ge 12.4){return 'cu124'}elseif($v -ge 12.1){return 'cu121'}elseif($v -ge 11.8){return 'cu118'}else{return $null}
}
$py=Get-PythonExe
Write-Host "python: $py"
# quick check
try{$ok=& $py -c "import torch,sys;sys.exit(0 if getattr(torch,'cuda',None) and torch.cuda.is_available() else 1)";if($LASTEXITCODE -eq 0){Write-Host 'GPU torch already available';exit 0}}catch{}
# upgrade pip
& $py -m pip install -U pip
$slug=Get-CudaSlug
if($null -ne $slug){
  Write-Host "Installing torch with $slug"
  & $py -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/$slug
}else{
  Write-Host 'Installing CPU torch (no CUDA detected)'
  & $py -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
}
# verify
& $py -c "import torch,sys;print('torch',torch.__version__);print('cuda',torch.cuda.is_available());print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no-cuda')"
