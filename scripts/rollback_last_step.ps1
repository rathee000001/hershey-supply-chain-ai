cd D:\HersheySupplyChainAI
Copy-Item ".\artifacts\rollback\step17e_b6g_clean_1_disable_melt_20260513_201451\HeroChocolateMeltOverlay.tsx" ".\src\components\cinematic\HeroChocolateMeltOverlay.tsx" -Force
Remove-Item -Recurse -Force .\.next -ErrorAction SilentlyContinue
npm run build
Write-Host "Rolled back one chat patch: step17e_b6g_clean_1_disable_melt"
