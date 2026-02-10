Write-Host "📄 LIST.md を生成しています（docs/ 直下のみ）..." -ForegroundColor Cyan

$mdFiles = Get-ChildItem -Path "docs" -Filter "*.md" -File | Sort-Object Name
$listContent = @("| 番号 | ファイルパス |", "|---|---|")
$count = 0

foreach ($file in $mdFiles) {
    $relativePath = "docs/$($file.Name)"
    $listContent += "| $count | $relativePath |"
    $count++
}

$listContent | Out-File -FilePath "LIST.md" -Encoding utf8

Write-Host "✅ LIST.md を生成完了しました。" -ForegroundColor Green
