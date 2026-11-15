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
    expect(document.documentElement).toHaveAttribute("lang", "fi");
  });
});
