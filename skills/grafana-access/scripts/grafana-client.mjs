#!/usr/bin/env node

import { assertNodeVersion } from "./grafana-env.mjs";

assertNodeVersion();

function basicAuthHeader(user, password) {
  const token = Buffer.from(`${user}:${password}`, "utf8").toString("base64");
  return `Basic ${token}`;
}

function parseSetCookie(headerValue) {
  const cookies = new Map();
  if (!headerValue) return cookies;

  const parts = Array.isArray(headerValue) ? headerValue : [headerValue];
  for (const part of parts) {
    const [pair] = part.split(";");
    const separator = pair.indexOf("=");
    if (separator === -1) continue;
    const name = pair.slice(0, separator).trim();
    const value = pair.slice(separator + 1).trim();
    cookies.set(name, value);
  }
  return cookies;
}

function cookieHeader(cookies) {
  return [...cookies.entries()]
    .map(([name, value]) => `${name}=${value}`)
    .join("; ");
}

function mergeCookies(target, source) {
  for (const [name, value] of source.entries()) {
    target.set(name, value);
  }
}

export class GrafanaClient {
  #config;
  #cookies = new Map();
  #loggedIn = false;
  #timeoutMs;

  constructor(config, { timeoutMs = 30_000 } = {}) {
    this.#config = config;
    this.#timeoutMs = timeoutMs;
  }

  get config() {
    return this.#config;
  }

  #ingressAuthHeader() {
    return basicAuthHeader(
      this.#config.basicAuthUser,
      this.#config.basicAuthPassword,
    );
  }

  async #request(path, { method = "GET", body, headers = {} } = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.#timeoutMs);

    try {
      const response = await fetch(new URL(path.replace(/^\//, ""), `${this.#config.url}/`), {
        method,
        headers: {
          Accept: "application/json",
          ...(this.#config.basicAuthUser ? { Authorization: this.#ingressAuthHeader() } : {}),
          ...(this.#cookies.size > 0
            ? { Cookie: cookieHeader(this.#cookies) }
            : {}),
          ...headers,
        },
        body,
        signal: controller.signal,
        redirect: "manual",
      });

      mergeCookies(
        this.#cookies,
        parseSetCookie(
          response.headers.getSetCookie?.() ??
            response.headers.get("set-cookie"),
        ),
      );

      const contentType = response.headers.get("content-type") ?? "";
      const text = await response.text();
      let payload = null;

      if (text && contentType.includes("application/json")) {
        try { payload = JSON.parse(text); }
        catch { throw new Error("Grafana returned malformed JSON; response body suppressed."); }
      } else if (text) {
        payload = text;
      }

      return { response, payload, text };
    } finally {
      clearTimeout(timer);
    }
  }

  async login() {
    const { response, payload } = await this.#request("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user: this.#config.username,
        password: this.#config.password,
      }),
    });

    if (response.status === 401 || response.status === 403) {
      throw new Error(`Grafana login failed (${response.status})`);
    }

    if (!response.ok && response.status !== 302) {
      throw new Error(`Grafana login failed (${response.status})`);
    }

    if (!this.#cookies.has("grafana_session")) throw new Error("Grafana did not return a session cookie; this helper requires password login.");
    this.#loggedIn = true;
    return {
      status: response.status,
      hasSession: this.#cookies.has("grafana_session"),
    };
  }

  async ensureLogin() {
    if (!this.#loggedIn) {
      await this.login();
    }
  }

  async health() {
    const { response, payload } = await this.#request("/api/health");
    return {
      ok: response.ok,
      status: response.status,
      database: payload?.database ?? null,
      version: payload?.version ?? null,
    };
  }

  async listDatasources() {
    await this.ensureLogin();
    const { response, payload } = await this.#request("/api/datasources");

    if (!response.ok) {
      throw new Error(
        `Failed to list datasources (${response.status})`,
      );
    }

    if (!Array.isArray(payload)) throw new Error("Unexpected Grafana datasource response.");
    return payload;
  }

  async findDatasourceByType(type, preferredNames = [type]) {
    const datasources = await this.listDatasources();
    const sources = datasources.filter((item) => item.type === type);

    if (sources.length === 0) {
      throw new Error(`No ${type} datasource found in Grafana`);
    }

    if (sources.length !== 1) throw new Error(`Multiple ${type} datasources found; configure a single relevant datasource or use the project-specific access adapter.`);
    const preferred = sources[0];

    return {
      uid: preferred.uid,
      name: preferred.name,
      type: preferred.type,
      count: sources.length,
    };
  }

  async findLokiDatasource() {
    return this.findDatasourceByType("loki", ["loki"]);
  }

  async findPrometheusDatasource() {
    return this.findDatasourceByType("prometheus", [
      "prometheus",
      "prom",
      "mimir",
    ]);
  }

  async queryLogs({
    expr,
    from = "now-1h",
    to = "now",
    limit = 1000,
    lokiUid,
  }) {
    await this.ensureLogin();

    const datasource = lokiUid ?? (await this.findLokiDatasource()).uid;
    const body = {
      queries: [
        {
          refId: "A",
          expr,
          queryType: "range",
          datasource: { type: "loki", uid: datasource },
          maxLines: limit,
        },
      ],
      from,
      to,
    };

    const { response, payload } = await this.#request("/api/ds/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(
        `Log query failed (${response.status})`,
      );
    }

    if (!payload?.results || typeof payload.results !== "object" || !payload.results.A) throw new Error("Unexpected Grafana log response; cannot establish query outcome.");
    if (Object.values(payload?.results ?? {}).some(result => result.error || result.status >= 400)) throw new Error("Grafana datasource query failed; inspect the query and datasource in the authorized interface.");
    return {
      datasourceUid: datasource,
      expr,
      from,
      to,
      limit,
      entries: normalizeLogEntries(payload),
      raw: payload,
    };
  }

  async prometheusApi({ path, params = {}, prometheusUid }) {
    await this.ensureLogin();

    const datasource =
      prometheusUid ?? (await this.findPrometheusDatasource()).uid;
    const search = new URLSearchParams();

    for (const [key, value] of Object.entries(params)) {
      if (value == null) continue;
      if (Array.isArray(value)) {
        for (const item of value) {
          if (item != null) search.append(key, String(item));
        }
      } else {
        search.set(key, String(value));
      }
    }

    const query = search.toString();
    const proxiedPath = `/api/datasources/proxy/uid/${encodeURIComponent(
      datasource,
    )}${path}${query ? `?${query}` : ""}`;

    const { response, payload } = await this.#request(proxiedPath);

    if (!response.ok) {
      throw new Error(
        `Prometheus query failed (${response.status})`,
      );
    }

    if (payload?.status !== "success" || !payload.data) {
      throw new Error(`Prometheus query failed`);
    }

    return {
      datasourceUid: datasource,
      raw: payload,
      data: payload?.data ?? null,
    };
  }

  async queryMetricsInstant({ expr, time, prometheusUid }) {
    const result = await this.prometheusApi({
      prometheusUid,
      path: "/api/v1/query",
      params: {
        query: expr,
        time,
      },
    });

    return {
      datasourceUid: result.datasourceUid,
      expr,
      time,
      resultType: result.data?.resultType ?? null,
      result: result.data?.result ?? [],
      raw: result.raw,
    };
  }

  async queryMetricsRange({ expr, start, end, step, prometheusUid }) {
    const result = await this.prometheusApi({
      prometheusUid,
      path: "/api/v1/query_range",
      params: {
        query: expr,
        start,
        end,
        step,
      },
    });

    return {
      datasourceUid: result.datasourceUid,
      expr,
      start,
      end,
      step,
      resultType: result.data?.resultType ?? null,
      result: result.data?.result ?? [],
      raw: result.raw,
    };
  }

  async metricSeries({ match, start, end, prometheusUid }) {
    const selectors = Array.isArray(match) ? match : [match];
    const result = await this.prometheusApi({
      prometheusUid,
      path: "/api/v1/series",
      params: {
        "match[]": selectors,
        start,
        end,
      },
    });

    return {
      datasourceUid: result.datasourceUid,
      match: selectors,
      start,
      end,
      series: Array.isArray(result.data) ? result.data : [],
      raw: result.raw,
    };
  }
}

function normalizeLogEntries(payload) {
  const entries = [];
  const results = payload?.results ?? {};

  for (const result of Object.values(results)) {
    const frames = result?.frames ?? [];
    for (const frame of frames) {
      entries.push(...entriesFromFrame(frame));
    }
  }

  entries.sort((left, right) => {
    const leftTs = Date.parse(left.timestamp ?? "") || 0;
    const rightTs = Date.parse(right.timestamp ?? "") || 0;
    return leftTs - rightTs;
  });

  return entries;
}

function entriesFromFrame(frame) {
  const fields = frame?.schema?.fields ?? [];
  const values = frame?.data?.values ?? [];

  if (fields.length === 0 || values.length === 0) {
    return [];
  }

  const fieldIndex = Object.fromEntries(
    fields.map((field, index) => [field.name, index]),
  );

  const timeIndex =
    fieldIndex.Time ??
    fieldIndex.timestamp ??
    fieldIndex.time ??
    fields.findIndex((field) => field.type === "time");

  const lineIndex =
    fieldIndex.Line ??
    fieldIndex.line ??
    fieldIndex.body ??
    fieldIndex.message ??
    fields.findIndex((field) => field.name === "Line" || field.name === "line");

  const labelsIndex =
    fieldIndex.labels ??
    fieldIndex.Labels ??
    fields.findIndex((field) => field.name === "labels");

  const rowCount = values[0]?.length ?? 0;
  const entries = [];

  for (let row = 0; row < rowCount; row += 1) {
    const timestampRaw = timeIndex >= 0 ? values[timeIndex]?.[row] : undefined;
    const line = lineIndex >= 0 ? values[lineIndex]?.[row] : undefined;
    const labelsRaw = labelsIndex >= 0 ? values[labelsIndex]?.[row] : undefined;

    entries.push({
      timestamp: normalizeTimestamp(timestampRaw),
      line: line == null ? "" : String(line),
      labels: normalizeLabels(labelsRaw, frame?.schema?.meta?.custom?.labels),
    });
  }

  return entries;
}

function normalizeTimestamp(value) {
  if (value == null) return null;
  if (typeof value === "number") {
    const millis = value > 1e12 ? value : value * 1000;
    return new Date(millis).toISOString();
  }
  const parsed = Date.parse(String(value));
  return Number.isNaN(parsed) ? String(value) : new Date(parsed).toISOString();
}

function normalizeLabels(raw, fallback) {
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    return raw;
  }

  if (typeof raw === "string") {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") return parsed;
    } catch {
      return { raw };
    }
  }

  if (fallback && typeof fallback === "object") {
    return fallback;
  }

  return {};
}
