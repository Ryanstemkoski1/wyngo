function timeLimitCountdown(init=false) {
  const el = document.querySelector("#reservation_form > div > fieldset > div.form-row.field-remaining_time > div > div > div");
  let seconds;
  if (init) {
      seconds = parseInt(el.innerText);
      el.dataset.initial = seconds;
  } else {
      seconds = parseInt(el.dataset.initial) - 1;
      el.dataset.initial = seconds;
  }
  if (!seconds) {
    return;
  }

  if (seconds <= 0) {
    el.innerHTML = `<div>
        <span style="font-size: 2em; font-weight: bold;">0</span>
        <span style="font-size: 1em; color: gray;">minutes</span>
        <span style="font-size: 2em; font-weight: bold;">0</span>
        <span style="font-size: 1em; color: gray;">seconds</span>
        <span style="font-size: 2em; font-weight: bold;">left</span>
    </div>`;
    return;
  }

  const minutes = Math.floor(seconds / 60); // Calculate minutes
  const remainingSeconds = seconds % 60; // Calculate remaining seconds

  // Ensure double-digit format for minutes and seconds
  const formattedMinutes = minutes.toString().padStart(2, '0');
  const formattedSeconds = remainingSeconds.toString().padStart(2, '0');

  el.innerHTML = `<div>
        <span style="font-size: 2em; font-weight: bold;">${formattedMinutes}</span>
        <span style="font-size: 1em; color: gray;">minutes</span>
        <span style="font-size: 2em; font-weight: bold;">${formattedSeconds}</span>
        <span style="font-size: 1em; color: gray;">seconds</span>
        <span style="font-size: 2em; font-weight: bold;">left</span>
    </div>`;
};

document.addEventListener("DOMContentLoaded", function () {
  if (location.pathname.includes("/admin/inventories/reservation/") &&
    location.pathname.includes("/change")) {
    timeLimitCountdown(true);
    setInterval(() => timeLimitCountdown(false), 1000);
  }
});
