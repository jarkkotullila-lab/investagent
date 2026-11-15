*** Settings ***
Library    Browser

*** Variables ***
${APP_NAME}    css=[data-testid="app-name"]
${BACKEND_STATUS}    css=[data-testid="backend-status"]
${LANGUAGE_SELECTOR}    css=[data-testid="language-selector"]
${RETRY_STATUS_BUTTON}    css=[data-testid="retry-status"]

*** Keywords ***
Dashboard Application Name Should Be
    [Arguments]    ${expected_name}
    ${actual_name}=    Get Text    ${APP_NAME}
    Should Be Equal As Strings    ${actual_name}    ${expected_name}

Dashboard Backend Status Should Be
    [Arguments]    ${expected_status}    ${expected_text}
    Wait For Elements State
    ...    css=[data-testid="backend-status"][data-status="${expected_status}"]
    ...    visible
    ...    10s
    ${actual_text}=    Get Text    ${BACKEND_STATUS}
    Should Be Equal As Strings    ${actual_text}    ${expected_text}

Select Dashboard Language
    [Arguments]    ${language}
    Select Options By    ${LANGUAGE_SELECTOR}    value    ${language}

Dashboard Document Language Should Be
    [Arguments]    ${expected_language}
    Get Attribute    html    lang    ==    ${expected_language}

Retry Dashboard Backend Connection
    Click    ${RETRY_STATUS_BUTTON}

Make Dashboard Health Endpoint Unavailable
    Evaluate JavaScript    ${None}
    ...    (originalFetch => {
    ...        window.fetch = (input, init) => {
    ...            const requestUrl = input instanceof Request ? input.url : String(input);
    ...            if (new URL(requestUrl, window.location.href).pathname === "/api/v1/health") {
    ...                return Promise.reject(new TypeError("Health endpoint unavailable"));
    ...            }
    ...            return originalFetch(input, init);
    ...        };
    ...    })(window.fetch.bind(window))
