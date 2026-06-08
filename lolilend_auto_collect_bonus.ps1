$headers = @{
    "accept" = "*/*"
    "access-id" = ""
    "access-token" = ""
    "referer" = "https://loliland.ru/ru/cabinet/bonus"
}

$cookies = @{
    "access_id" = ""
    "access_token" = ""
}

$response = Invoke-WebRequest -Uri "https://loliland.ru/apiv2/bonus/give" `
                               -Method POST `
                               -Headers $headers `
                               -WebSession (New-Object Microsoft.PowerShell.Commands.WebRequestSession)

$response.Content
