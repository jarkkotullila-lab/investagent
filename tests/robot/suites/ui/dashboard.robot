*** Settings ***
Resource         ../../resources/business/dashboard.resource
Resource         ../../resources/common/browser_setup.resource
Test Setup       Start Dashboard Browser Session
Test Teardown    Finish Dashboard Browser Session

*** Test Cases ***
Dashboard Displays The Application Name
    [Tags]    smoke    ui
    Dashboard Should Display Its Application Name

Dashboard Shows The Backend Online
    [Tags]    smoke    ui
    Dashboard Should Report The Backend Online

Dashboard Shows The Backend Offline When The Connection Is Lost
    [Tags]    ui
    Dashboard Should Report The Backend Online
    Simulate An Unavailable Backend
    Dashboard Should Report The Backend Offline

Dashboard Supports English And Finnish
    [Tags]    ui
    Dashboard Should Report The Backend Online
    Switch Dashboard Language To Finnish
    Switch Dashboard Language To English
