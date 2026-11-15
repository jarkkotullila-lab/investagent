*** Settings ***
Resource    ../../resources/api/health_api.resource

*** Test Cases ***
InvestAgent API Should Be Healthy
    [Tags]    smoke    api
    API Health Should Be OK
