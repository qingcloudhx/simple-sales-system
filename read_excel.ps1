$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $workbook = $excel.Workbooks.Open("C:\Users\xingh\Desktop\武汉赛维尔生物产品目录20260306.xlsx")
    $worksheet = $workbook.Sheets.Item(1)

    Write-Host "============================================================"
    Write-Host "Excel表头 (第一行):"
    Write-Host "============================================================"

    $headers = @()
    $col = 1
    while ($worksheet.Cells.Item(1, $col).Value() -ne $null) {
        $header = $worksheet.Cells.Item(1, $col).Value()
        $headers += $header
        Write-Host "$col. $header"
        $col++
    }

    Write-Host ""
    Write-Host "============================================================"
    Write-Host "前3行数据预览:"
    Write-Host "============================================================"

    for ($row = 2; $row -le 4; $row++) {
        $rowData = @()
        for ($i = 1; $i -le $headers.Count; $i++) {
            $val = $worksheet.Cells.Item($row, $i).Value()
            if ($val -eq $null) { $val = "" }
            $rowData += $val.ToString().Substring(0, [Math]::Min(30, $val.ToString().Length))
        }
        Write-Host "Row $($row-1): $($rowData -join ' | ')"
    }

    Write-Host ""
    Write-Host "============================================================"
    Write-Host "CSV Target Headers:"
    Write-Host "============================================================"
    Write-Host "1. Chinese Name"
    Write-Host "2. English Name"
    Write-Host "3. Sales Price"
    Write-Host "4. Stock"
    Write-Host "5. Category"
    Write-Host "6. SKU"
    Write-Host "7. Cost Price"
    Write-Host "8. Market Price"
    Write-Host "9. Image URL"

    $workbook.Close($false)
} finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}
