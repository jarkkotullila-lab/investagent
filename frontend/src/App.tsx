import { useEffect, useState, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import "./i18n";
import "./App.css";

type BackendStatus = "loading" | "online" | "offline";
type ResearchState =
  | "idle"
  | "loading"
  | "success"
  | "validation-error"
  | "backend-unavailable"
  | "provider-disabled"
  | "api-error";

interface ResearchAnalysis {
  company_name: string;
  summary: string;
  opportunities: string[];
  risks: string[];
  source_references: string[];
}

function isResearchAnalysis(value: unknown): value is ResearchAnalysis {
  return (
    typeof value === "object" &&
    value !== null &&
    "company_name" in value &&
    typeof value.company_name === "string" &&
    "summary" in value &&
    typeof value.summary === "string" &&
    "opportunities" in value &&
    Array.isArray(value.opportunities) &&
    value.opportunities.every((item) => typeof item === "string") &&
    "risks" in value &&
    Array.isArray(value.risks) &&
    value.risks.every((item) => typeof item === "string") &&
    "source_references" in value &&
    Array.isArray(value.source_references) &&
    value.source_references.every((item) => typeof item === "string")
  );
}

function App() {
  const { i18n, t } = useTranslation();
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("loading");
  const [healthCheckSequence, setHealthCheckSequence] = useState(0);
  const [companyName, setCompanyName] = useState("");
  const [sourceId, setSourceId] = useState("");
  const [sourceText, setSourceText] = useState("");
  const [researchState, setResearchState] = useState<ResearchState>("idle");
  const [analysis, setAnalysis] = useState<ResearchAnalysis | null>(null);
  const language = i18n.resolvedLanguage === "fi" ? "fi" : "en";

  useEffect(() => {
    const controller = new AbortController();

    fetch("/api/v1/health", { signal: controller.signal })
      .then((response) => {
        if (!controller.signal.aborted) {
          setBackendStatus(response.ok ? "online" : "offline");
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setBackendStatus("offline");
        }
      });

    return () => controller.abort();
  }, [healthCheckSequence]);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  function retryHealthCheck() {
    setBackendStatus("loading");
    setHealthCheckSequence((sequence) => sequence + 1);
  }

  async function submitResearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (researchState === "loading") {
      return;
    }

    const request = {
      company_name: companyName.trim(),
      sources: [{ source_id: sourceId.trim(), text: sourceText.trim() }],
    };
    setAnalysis(null);
    if (!request.company_name || !request.sources[0].source_id || !request.sources[0].text) {
      setResearchState("validation-error");
      return;
    }

    setResearchState("loading");
    let response: Response;
    try {
      response = await fetch("/api/v1/research/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });
    } catch {
      setResearchState("backend-unavailable");
      return;
    }

    if (response.status === 501) {
      setResearchState("provider-disabled");
      return;
    }
    if (response.status === 422) {
      setResearchState("validation-error");
      return;
    }
    if (response.status === 503) {
      setResearchState("backend-unavailable");
      return;
    }
    if (!response.ok) {
      setResearchState("api-error");
      return;
    }

    let result: unknown;
    try {
      result = await response.json();
    } catch {
      setResearchState("api-error");
      return;
    }
    if (!isResearchAnalysis(result)) {
      setResearchState("api-error");
      return;
    }

    setAnalysis(result);
    setResearchState("success");
  }

  const hasResearchError =
    researchState === "validation-error" ||
    researchState === "backend-unavailable" ||
    researchState === "provider-disabled" ||
    researchState === "api-error";

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1 data-testid="app-name">{t("appName")}</h1>
        <div className="language-control">
          <label htmlFor="language-selector">{t("language.label")}</label>
          <select
            id="language-selector"
            data-testid="language-selector"
            value={language}
            onChange={(event) => void i18n.changeLanguage(event.currentTarget.value)}
          >
            <option value="en">{t("language.english")}</option>
            <option value="fi">{t("language.finnish")}</option>
          </select>
        </div>
      </header>

      <main className="dashboard">
        <section className="welcome-panel" aria-labelledby="dashboard-title">
          <p className="eyebrow">{t("dashboard.eyebrow")}</p>
          <h2 id="dashboard-title" data-testid="dashboard-title">
            {t("dashboard.title")}
          </h2>
          <p className="dashboard-description">{t("dashboard.description")}</p>
        </section>

        <section className="connection-card" aria-labelledby="backend-title">
          <div>
            <h2 id="backend-title">{t("backend.title")}</h2>
            <p className="connection-description">{t("backend.description")}</p>
          </div>
          <div
            className={`backend-status backend-status--${backendStatus}`}
            data-testid="backend-status"
            data-status={backendStatus}
            role="status"
            aria-live="polite"
          >
            <span className="status-indicator" aria-hidden="true" />
            <span>{t(`backend.status.${backendStatus}`)}</span>
          </div>
          <button
            className="retry-button"
            data-testid="retry-status"
            type="button"
            disabled={backendStatus === "loading"}
            onClick={retryHealthCheck}
          >
            {t("backend.retry")}
          </button>
        </section>

        <section className="research-card" aria-labelledby="research-title">
          <div className="research-heading">
            <h2 id="research-title">{t("research.title")}</h2>
            <p>{t("research.description")}</p>
          </div>
          <form
            className="research-form"
            data-testid="research-form"
            noValidate
            onSubmit={(event) => void submitResearch(event)}
          >
            <div className="research-field">
              <label htmlFor="research-company-name">{t("research.companyName")}</label>
              <input
                id="research-company-name"
                data-testid="research-company-name"
                type="text"
                required
                value={companyName}
                aria-invalid={researchState === "validation-error" && !companyName.trim()}
                aria-describedby={
                  researchState === "validation-error" && !companyName.trim()
                    ? "research-status"
                    : undefined
                }
                onChange={(event) => setCompanyName(event.currentTarget.value)}
              />
            </div>
            <div className="research-field">
              <label htmlFor="research-source-id">{t("research.sourceId")}</label>
              <input
                id="research-source-id"
                data-testid="research-source-id"
                type="text"
                required
                value={sourceId}
                aria-invalid={researchState === "validation-error" && !sourceId.trim()}
                aria-describedby={
                  researchState === "validation-error" && !sourceId.trim()
                    ? "research-status"
                    : undefined
                }
                onChange={(event) => setSourceId(event.currentTarget.value)}
              />
            </div>
            <div className="research-field research-field--wide">
              <label htmlFor="research-source-text">{t("research.sourceText")}</label>
              <textarea
                id="research-source-text"
                data-testid="research-source-text"
                required
                rows={5}
                value={sourceText}
                aria-invalid={researchState === "validation-error" && !sourceText.trim()}
                aria-describedby={
                  researchState === "validation-error" && !sourceText.trim()
                    ? "research-status"
                    : undefined
                }
                onChange={(event) => setSourceText(event.currentTarget.value)}
              />
            </div>
            <button
              className="analyze-button"
              data-testid="research-submit"
              type="submit"
              disabled={researchState === "loading"}
            >
              {researchState === "loading"
                ? t("research.analyzing")
                : t("research.analyze")}
            </button>
          </form>

          <p
            className={`research-status research-status--${hasResearchError ? "error" : "normal"}`}
            data-testid="research-status"
            data-state={researchState}
            role={hasResearchError ? "alert" : "status"}
            aria-live="polite"
          >
            {t(`research.status.${researchState}`)}
          </p>

          {analysis && (
            <section
              className="research-result"
              aria-labelledby="research-result-title"
              data-testid="research-result"
            >
              <h3 id="research-result-title">{t("research.result.title")}</h3>
              <dl className="research-result-details">
                <div>
                  <dt>{t("research.result.companyName")}</dt>
                  <dd data-testid="analysis-company-name">{analysis.company_name}</dd>
                </div>
                <div>
                  <dt>{t("research.result.summary")}</dt>
                  <dd data-testid="analysis-summary">{analysis.summary}</dd>
                </div>
              </dl>
              <div className="research-result-lists">
                <div>
                  <h4>{t("research.result.opportunities")}</h4>
                  <ul data-testid="analysis-opportunities">
                    {analysis.opportunities.map((opportunity, index) => (
                      <li key={`${opportunity}-${index}`}>{opportunity}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4>{t("research.result.risks")}</h4>
                  <ul data-testid="analysis-risks">
                    {analysis.risks.map((risk, index) => (
                      <li key={`${risk}-${index}`}>{risk}</li>
                    ))}
                  </ul>
                </div>
              </div>
              <div>
                <h4>{t("research.result.sourceReferences")}</h4>
                <ul data-testid="analysis-source-references">
                  {analysis.source_references.map((reference, index) => (
                    <li key={`${reference}-${index}`}>{reference}</li>
                  ))}
                </ul>
              </div>
            </section>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
