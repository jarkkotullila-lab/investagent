import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import "./i18n";
import "./App.css";

type BackendStatus = "loading" | "online" | "offline";

function App() {
  const { i18n, t } = useTranslation();
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("loading");
  const [healthCheckSequence, setHealthCheckSequence] = useState(0);
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
      </main>
    </div>
  );
}

export default App;
