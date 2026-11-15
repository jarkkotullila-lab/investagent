*** Settings ***
Resource    ../pages/dashboard_page.resource

*** Keywords ***
Dashboard Should Display Its Application Name
    Dashboard Application Name Should Be    InvestAgent

Dashboard Should Report The Backend Online
    Dashboard Backend Status Should Be    online    Backend is online

Dashboard Should Report The Backend Offline
    Dashboard Backend Status Should Be    offline    Backend is offline

Switch Dashboard Language To Finnish
    Select Dashboard Language    fi
    Dashboard Document Language Should Be    fi
    Dashboard Backend Status Should Be    online    Taustapalvelu on käytettävissä

Switch Dashboard Language To English
    Select Dashboard Language    en
    Dashboard Document Language Should Be    en
    Dashboard Backend Status Should Be    online    Backend is online

Simulate An Unavailable Backend
    Make Dashboard Health Endpoint Unavailable
    Retry Dashboard Backend Connection
