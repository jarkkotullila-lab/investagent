*** Settings ***
Library     RequestsLibrary
Resource    ../common/api_config.resource

*** Keywords ***
API Research Analysis Should Report Not Implemented Yet
    Create Session    investagent-research    ${API_BASE_URL}
    ${source}=    Create Dictionary
    ...    source_id=synthetic-source-1
    ...    text=Synthetic research note for API contract testing.
    ${sources}=    Create List    ${source}
    ${request}=    Create Dictionary
    ...    company_name=Example Corporation
    ...    sources=${sources}
    ${response}=    POST On Session
    ...    investagent-research
    ...    /api/v1/research/analyze
    ...    json=${request}
    ...    expected_status=anything
    Should Be Equal As Integers    ${response.status_code}    501
    ${expected}=    Create Dictionary    detail=Research analysis is not implemented yet.
    Should Be Equal    ${response.json()}    ${expected}
