*** Settings ***
Library    Browser

*** Variables ***
${FRONTEND_BASE_URL}    http://127.0.0.1:5173

*** Keywords ***
Start Dashboard Browser Session
    New Browser    chromium    headless=True    reuse_existing=False
    New Context
    New Page    ${FRONTEND_BASE_URL}

Finish Dashboard Browser Session
    ${browser_ids}=    Get Browser Ids
    IF    $browser_ids
        Run Keyword If Test Failed    Take Screenshot    EMBED
        Close Browser    ALL
    END
