*** Settings ***
Library     RequestsLibrary
Resource    ../common/api_config.resource

*** Keywords ***
API Health Should Be OK
    Create Session    investagent    ${API_BASE_URL}
    ${response}=    GET On Session    investagent    /api/v1/health
    Should Be Equal As Integers    ${response.status_code}    200
    ${expected}=    Create Dictionary    status=ok    service=investagent-api    version=0.1.0
    Should Be Equal    ${response.json()}    ${expected}
