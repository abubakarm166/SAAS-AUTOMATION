/**
 * Extract likely US street addresses from visible page text.
 * Simplified port of legacy auction-page scraping heuristics.
 */
const STREET_WORDS =
  "st|street|ave|avenue|rd|road|dr|drive|ln|lane|blvd|boulevard|ct|court|way|place|pl|plz|plaza|cir|circle|trl|trail|pkwy|parkway|ter|terrace|hwy|highway";

const ADDRESS_REGEX = new RegExp(
  String.raw`\b(\d{1,6}\s+[A-Za-z0-9#.\s'/-]{2,50}?\s*(?:${STREET_WORDS})\.?)[,]?\s+([A-Za-z][A-Za-z\s.'-]{1,40}),?\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b`,
  "gi",
);

function normalizeAddress(match) {
  const street = match[1].replace(/\s+/g, " ").trim();
  const city = match[2].replace(/\s+/g, " ").trim();
  const state = match[3].toUpperCase();
  const zip = match[4];
  return `${street}, ${city}, ${state} ${zip}`;
}

function extractAddresses(text) {
  if (!text) return [];
  const collapsed = text.replace(/\s+/g, " ");
  const found = new Set();
  let match;
  while ((match = ADDRESS_REGEX.exec(collapsed)) !== null) {
    found.add(normalizeAddress(match));
  }
  return [...found];
}

function extractAddressesFromDocument(doc = document) {
  const bodyText = doc.body?.innerText || "";
  const title = doc.title || "";
  const metaDesc = doc.querySelector('meta[name="description"]')?.content || "";
  const combined = `${title}\n${metaDesc}\n${bodyText}`;
  return extractAddresses(combined);
}

if (typeof globalThis !== "undefined") {
  globalThis.extractAddresses = extractAddresses;
  globalThis.extractAddressesFromDocument = extractAddressesFromDocument;
}
