document.addEventListener("DOMContentLoaded", function () {
  function setLocale() {
    if (typeof Plotly !== "undefined") {
      // Set the Plotly default locale
      Plotly.setPlotConfig({ locale: "pt-BR" });
    } else {
      // Retry after a short delay
      setTimeout(setLocale, 50);
    }
  }

  // Attempt to set the locale
  setLocale();
});
