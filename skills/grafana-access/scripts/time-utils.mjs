const DURATION_UNITS = {
  s: 1000,
  m: 60 * 1000,
  h: 60 * 60 * 1000,
  d: 24 * 60 * 60 * 1000,
  w: 7 * 24 * 60 * 60 * 1000,
};

export function parseDurationMillis(value) {
  const text = String(value ?? "").trim();
  const match = text.match(/^(\d+(?:\.\d+)?)([smhdw])$/);

  if (!match) {
    throw new Error(`Invalid duration "${value}". Use values like 30s, 5m, 1h, 7d.`);
  }

  return Number.parseFloat(match[1]) * DURATION_UNITS[match[2]];
}

export function parseTimeToUnixSeconds(value, now = Date.now()) {
  const text = String(value ?? "").trim();

  if (!text || text === "now") {
    return Math.floor(now / 1000);
  }

  const relative = text.match(/^now-([0-9]+(?:\.[0-9]+)?[smhdw])$/);
  if (relative) {
    return Math.floor((now - parseDurationMillis(relative[1])) / 1000);
  }

  if (/^\d+(?:\.\d+)?$/.test(text)) {
    return text;
  }

  const parsed = Date.parse(text);
  if (Number.isNaN(parsed)) {
    throw new Error(
      `Invalid time "${value}". Use now, now-1h, Unix seconds, or an ISO timestamp.`,
    );
  }

  return Math.floor(parsed / 1000);
}

export function normalizePrometheusStep(value) {
  const text = String(value ?? "").trim();
  if (!text) return "60s";

  if (/^\d+(?:\.\d+)?$/.test(text)) {
    return text;
  }

  parseDurationMillis(text);
  return text;
}
