function getID(element) {
  id = element.getAttribute("id").split("_")[1];
  return id;
}

function favoriteBtn(element) {
  const favoriteID = getID(element);
  const favoriteIcon = document.getElementById(`favorite_${favoriteID}`);
  favoriteIcon.classList.toggle("fill-white");
}

const openDrawerButton = document.getElementById("openDrawer");
const closeDrawerButton = document.getElementById("closeDrawer");
const overlay = document.getElementById("overlay");
const drawer = document.getElementById("drawer");

if (openDrawerButton) {
  openDrawerButton.addEventListener("click", () => {
    overlay.style.opacity = "0.6";
    drawer.style.height = `445px`;
    document.body.classList.add("overflow-hidden");
  });

  closeDrawerButton.addEventListener("click", () => {
    overlay.style.opacity = "0";
    drawer.style.height = "0";
    document.body.classList.remove("overflow-hidden");
  });
}

function infiniteScroll() {
  var mobileContainer = document.getElementById("mobile-container");
  var tabletContainer = document.getElementById("tablet-container");

  if (mobileContainer || tabletContainer) {
    var mobileComputedStyle = window.getComputedStyle(mobileContainer);
    var tabletComputedStyle = window.getComputedStyle(tabletContainer);
    var loading = document.querySelector('.loading-indicator');

    var infiniteList = new Waypoint.Infinite({
      element:
        mobileComputedStyle.display !== "none"
          ? ".infinite-container-mobile"
          : tabletComputedStyle.display !== "none"
          ? ".infinite-container-tablet"
          : ".infinite-container-desktop",
      items:
        mobileComputedStyle.display !== "none"
          ? ".infinite-item-mobile"
          : tabletComputedStyle.display !== "none"
          ? ".infinite-item-tablet"
          : ".infinite-item-desktop",
      more:
        mobileComputedStyle.display !== "none"
          ? ".infinite-more-link-mobile"
          : tabletComputedStyle.display !== "none"
          ? ".infinite-more-link-tablet"
          : ".infinite-more-link-desktop",
      onlyOnScroll: true,
      loadingClass: 'infinite-loading',
      onBeforePageLoad: function () {
        loading.classList.remove('hidden');
      },
      onAfterPageLoad: function () {
        loading.classList.add('hidden');
      }
    });
  } else {
    var infinite = new Waypoint.Infinite({
      element: $(".infinite-container")[0],
      offset: "bottom-in-view",
      loadingClass: 'infinite-loading',
      onBeforePageLoad: function () {
        loading.classList.remove('hidden');
      },
      onAfterPageLoad: function () {
        loading.classList.add('hidden');
      }
    });
  }
}

window.addEventListener("load", infiniteScroll);
//window.addEventListener("resize", infiniteScroll);

let valueCount;

function plusBtn(element) {
  id = getID(element);

  valueCount = document.getElementById(`quantity_${id}`).value;

  valueCount++;

  document.getElementById(`quantity_${id}`).value = valueCount;
  quantityMax = document.getElementById(`quantity_${id}`).getAttribute("max");

  if (valueCount > 1) {
    document.getElementById(`minus_${id}`).removeAttribute("disabled");
  }

  if (valueCount >= quantityMax) {
    element.setAttribute("disabled", "disabled");
  } else if (valueCount < quantityMax) {
    element.removeAttribute("disabled");
  }
}

function minusBtn(element) {
  id = getID(element);
  valueCount = document.getElementById(`quantity_${id}`).value;

  valueCount--;

  document.getElementById(`quantity_${id}`).value = valueCount;
  quantityMax = document.getElementById(`quantity_${id}`).getAttribute("max");

  if (valueCount == 1) {
    element.setAttribute("disabled", "disabled");
  }

  if (valueCount < quantityMax) {
    document.getElementById(`plus_${id}`).removeAttribute("disabled");
  }
}

function rangePriceSlider(input, rangeInput, rangePrice, range, rangeMin) {
  input.addEventListener("input", (e) => {
    let minRange = parseInt(rangeInput[0].value);
    let maxRange = parseInt(rangeInput[1].value);
    if (maxRange - minRange < rangeMin) {
      if (e.target.className === "min") {
        rangeInput[0].value = maxRange - rangeMin;
      } else {
        rangeInput[1].value = minRange + rangeMin;
      }
    } else {
      rangePrice[0].textContent = `$${minRange}.00`;
      rangePrice[1].textContent = `$${maxRange}.00`;
      range.style.left = (minRange / rangeInput[0].max) * 100 + "%";
      range.style.right = 100 - (maxRange / rangeInput[1].max) * 100 + "%";
    }
  });
}

const range = document.querySelector(".price-range-selected");
const rangeInput = document.querySelectorAll(".price-range-input input");
const rangePrice = document.querySelectorAll(".price-range-price span");

rangeInput.forEach((input) => {
  rangePriceSlider(input, rangeInput, rangePrice, range, 15);
});

const rangeDesktop = document.querySelector(".selected-desktop");
const rangeInputDesktop = document.querySelectorAll(".input-desktop input");
const rangePriceDesktop = document.querySelectorAll(".price-desktop span");

rangeInputDesktop.forEach((input) => {
  rangePriceSlider(
    input,
    rangeInputDesktop,
    rangePriceDesktop,
    rangeDesktop,
    15
  );
});

const rangeTablet = document.querySelector(".selected-tablet");
const rangeInputTablet = document.querySelectorAll(".input-tablet input");
const rangePriceTablet = document.querySelectorAll(".price-tablet span");

rangeInputTablet.forEach((input) => {
  rangePriceSlider(input, rangeInputTablet, rangePriceTablet, rangeTablet, 15);
});

function reserveBtn(element) {
  id = getID(element);

  const form = document.getElementById(`make-res_${id}`);

  form.submit();

  const reserveBtn = document.getElementById(`reserve_${id}`);

  reserveBtn.setAttribute("disabled", "disabled");
  reserveBtn.classList.add("opacity-50");
}
const close = document.querySelector(".close-alert");

if (close) {
  close.addEventListener("click", function () {
    this.parentNode.classList.add("hidden");
  });
}