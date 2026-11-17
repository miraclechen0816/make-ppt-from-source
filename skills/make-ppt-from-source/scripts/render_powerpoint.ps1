param([string]$Source, [string]$Destination, [int]$Width = 1920, [int]$Height = 1080)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $Destination) { throw 'Choose a new render directory.' }
New-Item -ItemType Directory -Path $Destination | Out-Null
$officeApplication = New-Object -ComObject PowerPoint.Application
$document = $null
try {
    $document = $officeApplication.Presentations.Open($Source, $true, $false, $false)
    for ($index = 1; $index -le $document.Slides.Count; $index++) {
        $target = Join-Path $Destination ('slide_{0:D3}.png' -f $index)
        $document.Slides.Item($index).Export($target, 'PNG', $Width, $Height)
    }
} finally {
    if ($null -ne $document) { $document.Close() }
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($officeApplication) | Out-Null
}
