*** Settings ***
Resource    ../../resources/api/research_api.resource

*** Test Cases ***
InvestAgent Should Explain Research Analysis Is Not Available Yet
    [Tags]    api
    API Research Analysis Should Report Not Implemented Yet
