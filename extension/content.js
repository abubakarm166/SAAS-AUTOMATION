chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "extract_addresses") return;

  try {
    const addresses = extractAddressesFromDocument();
    sendResponse({
      ok: true,
      url: location.href,
      title: document.title,
      addresses,
    });
  } catch (error) {
    sendResponse({
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    });
  }
  return true;
});
