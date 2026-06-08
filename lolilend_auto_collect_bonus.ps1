$headers = @{
    "accept" = "*/*"
    "access-id" = "01887979-9a2f-7a20-b7f6-f2eb0ab21e80"
    "access-token" = "977641b99da52aa77325d3af8c6eb80e0cfb60d22cc8aed716b445fead4d83d0"
    "referer" = "https://loliland.ru/ru/cabinet/bonus"
}

$cookies = @{
    "access_id" = "01887979-9a2f-7a20-b7f6-f2eb0ab21e80"
    "access_token" = "977641b99da52aa77325d3af8c6eb80e0cfb60d22cc8aed716b445fead4d83d0"
}

$response = Invoke-WebRequest -Uri "https://loliland.ru/apiv2/bonus/give" `
                               -Method POST `
                               -Headers $headers `
                               -WebSession (New-Object Microsoft.PowerShell.Commands.WebRequestSession)

$response.Content