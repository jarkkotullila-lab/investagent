import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import i18n from "./i18n";

const mockFetch = vi.fn<typeof fetch>();

describe("dashboard", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("en");
    mockFetch.mockReset();
    vi.stubGlobal("fetch", mockFetch);
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("renders the dashboard and application name", async () => {
    mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

    render(<App />);

    expect(screen.getByTestId("app-name")).toHaveTextContent("InvestAgent");
    expect(screen.getByTestId("dashboard-title")).toHaveTextContent(
      "Your research workspace",
    );
    expect(screen.getByRole("combobox", { name: "Language" })).toBeInTheDocument();
  });

  it("shows a loading state while the health check is pending", () => {
    mockFetch.mockImplementation(() => new Promise<Response>(() => {}));

    render(<App />);

    expect(screen.getByTestId("backend-status")).toHaveAttribute(
      "data-status",
      "loading",
    );
  });

  it("shows the backend online when the health endpoint responds successfully", async () => {
    mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByTestId("backend-status")).toHaveAttribute(
        "data-status",
        "online",
      );
    });
  });

  it("shows the backend offline when the health endpoint cannot be reached", async () => {
    mockFetch.mockRejectedValue(new TypeError("Network unavailable"));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByTestId("backend-status")).toHaveAttribute(
        "data-status",
        "offline",
      );
    });
  });

  it("switches the dashboard language to Finnish", async () => {
    mockFetch.mockResolvedValue(new Response(null, { status: 200 }));
    const user = userEvent.setup();

    render(<App />);

    await user.selectOptions(screen.getByTestId("language-selector"), "fi");

    expect(screen.getByTestId("dashboard-title")).toHaveTextContent(
      "Tutkimustyötilasi",
    );
    expect(screen.getByRole("textbox", { name: "Yrityksen nimi" })).toBeInTheDocument();
    expect(document.documentElement).toHaveAttribute("lang", "fi");
  });

  it("renders the one-source research form", async () => {
    mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

    render(<App />);

    expect(screen.getByRole("textbox", { name: "Company name" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Source ID" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Source text" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze research" })).toBeInTheDocument();
    expect(screen.getByTestId("research-status")).toHaveAttribute(
      "data-state",
      "idle",
    );
  });

  it("shows a validation error when required research fields are empty", async () => {
    mockFetch.mockResolvedValue(new Response(null, { status: 200 }));
    const user = userEvent.setup();

    render(<App />);
    await user.click(screen.getByTestId("research-submit"));

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Enter a company name, source ID, and source text.",
    );
    expect(screen.getByTestId("research-status")).toHaveAttribute(
      "data-state",
      "validation-error",
    );
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it("submits one source and renders the research analysis", async () => {
    const analysis = {
      company_name: "Example Technologies",
      summary: "Synthetic company summary.",
      opportunities: ["Synthetic opportunity."],
      risks: ["Synthetic risk."],
      source_references: ["annual-report"],
    };
    mockFetch.mockImplementation((input) => {
      if (String(input) === "/api/v1/health") {
        return Promise.resolve(new Response(null, { status: 200 }));
      }
      return Promise.resolve(
        new Response(JSON.stringify(analysis), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );
    });
    const user = userEvent.setup();

    render(<App />);
    await user.type(screen.getByTestId("research-company-name"), "Example Technologies");
    await user.type(screen.getByTestId("research-source-id"), "annual-report");
    await user.type(
      screen.getByTestId("research-source-text"),
      "Synthetic research information.",
    );
    await user.click(screen.getByTestId("research-submit"));

    expect(await screen.findByTestId("research-result")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-company-name")).toHaveTextContent(
      "Example Technologies",
    );
    expect(screen.getByTestId("analysis-summary")).toHaveTextContent(
      "Synthetic company summary.",
    );
    expect(screen.getByTestId("analysis-opportunities")).toHaveTextContent(
      "Synthetic opportunity.",
    );
    expect(screen.getByTestId("analysis-risks")).toHaveTextContent("Synthetic risk.");
    expect(screen.getByTestId("analysis-source-references")).toHaveTextContent(
      "annual-report",
    );
    expect(mockFetch).toHaveBeenCalledWith("/api/v1/research/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        company_name: "Example Technologies",
        sources: [
          {
            source_id: "annual-report",
            text: "Synthetic research information.",
          },
        ],
      }),
    });
  });

  it("disables repeated submissions while analysis is loading", async () => {
    let resolveAnalysis: (response: Response) => void = () => {};
    const pendingAnalysis = new Promise<Response>((resolve) => {
      resolveAnalysis = resolve;
    });
    mockFetch.mockImplementation((input) => {
      if (String(input) === "/api/v1/health") {
        return Promise.resolve(new Response(null, { status: 200 }));
      }
      return pendingAnalysis;
    });
    const user = userEvent.setup();

    render(<App />);
    await user.type(screen.getByTestId("research-company-name"), "Example Technologies");
    await user.type(screen.getByTestId("research-source-id"), "annual-report");
    await user.type(
      screen.getByTestId("research-source-text"),
      "Synthetic research information.",
    );
    await user.click(screen.getByTestId("research-submit"));

    expect(screen.getByTestId("research-submit")).toBeDisabled();
    expect(screen.getByTestId("research-status")).toHaveAttribute(
      "data-state",
      "loading",
    );

    resolveAnalysis(
      new Response(
        JSON.stringify({
          company_name: "Example Technologies",
          summary: "Synthetic company summary.",
          opportunities: [],
          risks: [],
          source_references: ["annual-report"],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    expect(await screen.findByTestId("research-result")).toBeInTheDocument();
  });

  it("shows a specific message when the AI provider is disabled", async () => {
    mockFetch.mockImplementation((input) =>
      Promise.resolve(
        new Response(null, {
          status: String(input) === "/api/v1/health" ? 200 : 501,
        }),
      ),
    );
    const user = userEvent.setup();

    render(<App />);
    await user.type(screen.getByTestId("research-company-name"), "Example Technologies");
    await user.type(screen.getByTestId("research-source-id"), "annual-report");
    await user.type(
      screen.getByTestId("research-source-text"),
      "Synthetic research information.",
    );
    await user.click(screen.getByTestId("research-submit"));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "The AI provider is disabled.",
    );
    expect(screen.getByTestId("research-status")).toHaveAttribute(
      "data-state",
      "provider-disabled",
    );
  });

  it("shows a validation error for an invalid API request", async () => {
    mockFetch.mockImplementation((input) =>
      Promise.resolve(
        new Response(null, {
          status: String(input) === "/api/v1/health" ? 200 : 422,
        }),
      ),
    );
    const user = userEvent.setup();

    render(<App />);
    await user.type(screen.getByTestId("research-company-name"), "Example Technologies");
    await user.type(screen.getByTestId("research-source-id"), "annual-report");
    await user.type(
      screen.getByTestId("research-source-text"),
      "Synthetic research information.",
    );
    await user.click(screen.getByTestId("research-submit"));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Enter a company name, source ID, and source text.",
    );
  });

  it("shows a backend unavailable message for a network failure", async () => {
    mockFetch.mockImplementation((input) => {
      if (String(input) === "/api/v1/health") {
        return Promise.resolve(new Response(null, { status: 200 }));
      }
      return Promise.reject(new TypeError("Network unavailable"));
    });
    const user = userEvent.setup();

    render(<App />);
    await user.type(screen.getByTestId("research-company-name"), "Example Technologies");
    await user.type(screen.getByTestId("research-source-id"), "annual-report");
    await user.type(
      screen.getByTestId("research-source-text"),
      "Synthetic research information.",
    );
    await user.click(screen.getByTestId("research-submit"));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "The research service or local AI provider is unavailable.",
    );
    expect(screen.getByTestId("research-status")).toHaveAttribute(
      "data-state",
      "backend-unavailable",
    );
  });

  it("shows a generic message for other API errors", async () => {
    mockFetch.mockImplementation((input) =>
      Promise.resolve(
        new Response(null, {
          status: String(input) === "/api/v1/health" ? 200 : 500,
        }),
      ),
    );
    const user = userEvent.setup();

    render(<App />);
    await user.type(screen.getByTestId("research-company-name"), "Example Technologies");
    await user.type(screen.getByTestId("research-source-id"), "annual-report");
    await user.type(
      screen.getByTestId("research-source-text"),
      "Synthetic research information.",
    );
    await user.click(screen.getByTestId("research-submit"));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "The research request failed. Please try again.",
    );
    expect(screen.getByTestId("research-status")).toHaveAttribute(
      "data-state",
      "api-error",
    );
  });
});
