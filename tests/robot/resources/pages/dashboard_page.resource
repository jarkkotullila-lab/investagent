*** Settings ***
Library    Browser

*** Variables ***
${APP_NAME}    css=[data-testid="app-name"]
${BACKEND_STATUS}    css=[data-testid="backend-status"]
${LANGUAGE_SELECTOR}    css=[data-testid="language-selector"]
${RETRY_STATUS_BUTTON}    css=[data-testid="retry-status"]
${RESEARCH_COMPANY_NAME}    css=[data-testid="research-company-name"]
${RESEARCH_SOURCE_ID}    css=[data-testid="research-source-id"]
${RESEARCH_SOURCE_TEXT}    css=[data-testid="research-source-text"]
${RESEARCH_SUBMIT_BUTTON}    css=[data-testid="research-submit"]
${RESEARCH_RESULT}    css=[data-testid="research-result"]
${ANALYSIS_COMPANY_NAME}    css=[data-testid="analysis-company-name"]
${ANALYSIS_SUMMARY}    css=[data-testid="analysis-summary"]
${ANALYSIS_OPPORTUNITIES}    css=[data-testid="analysis-opportunities"]
${ANALYSIS_RISKS}    css=[data-testid="analysis-risks"]
${ANALYSIS_SOURCE_REFERENCES}    css=[data-testid="analysis-source-references"]

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

Fill Research Form
    [Arguments]    ${company_name}    ${source_id}    ${source_text}
    Fill Text    ${RESEARCH_COMPANY_NAME}    ${company_name}
    Fill Text    ${RESEARCH_SOURCE_ID}    ${source_id}
    Fill Text    ${RESEARCH_SOURCE_TEXT}    ${source_text}

Submit Research Form
    Click    ${RESEARCH_SUBMIT_BUTTON}

Research Analysis Should Match
    [Arguments]    ${company_name}    ${summary}    ${opportunity}    ${risk}    ${source_reference}
    Wait For Elements State    ${RESEARCH_RESULT}    visible    10s
    ${actual_company}=    Get Text    ${ANALYSIS_COMPANY_NAME}
    Should Be Equal As Strings    ${actual_company}    ${company_name}
    ${actual_summary}=    Get Text    ${ANALYSIS_SUMMARY}
    Should Be Equal As Strings    ${actual_summary}    ${summary}
    ${actual_opportunities}=    Get Text    ${ANALYSIS_OPPORTUNITIES}
    Should Contain    ${actual_opportunities}    ${opportunity}
    ${actual_risks}=    Get Text    ${ANALYSIS_RISKS}
    Should Contain    ${actual_risks}    ${risk}
    ${actual_sources}=    Get Text    ${ANALYSIS_SOURCE_REFERENCES}
    Should Contain    ${actual_sources}    ${source_reference}

Mock Research API Response
    Evaluate JavaScript    ${None}
    ...    (originalFetch => {
    ...        window.fetch = (input, init) => {
    ...            const requestUrl = input instanceof Request ? input.url : String(input);
    ...            if (new URL(requestUrl, window.location.href).pathname === "/api/v1/research/analyze") {
    ...                return Promise.resolve(new Response(JSON.stringify({
    ...                    company_name: "Example Technologies",
    ...                    summary: "Synthetic analysis based on the submitted research.",
    ...                    opportunities: ["Synthetic opportunity."],
    ...                    risks: ["Synthetic risk."],
    ...                    source_references: ["annual-report"]
    ...                }), { status: 200, headers: { "Content-Type": "application/json" } }));
    ...            }
    ...            return originalFetch(input, init);
    ...        };
    ...    })(window.fetch.bind(window))
