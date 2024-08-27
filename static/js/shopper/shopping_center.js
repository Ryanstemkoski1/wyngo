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

var infinite = new Waypoint.Infinite({
  element: $(".infinite-container")[0],
  offset: "bottom-in-view",
});

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

function sliders() {
  /* Swipper params */

  const swiperParams = {
    loop: false,
    breakpoints: {
      320: {
        slidesPerGroup: 1,
        spaceBetween: 16,
        slidesPerView: 1.5,
      },
      375: {
        slidesPerView: "auto",
        spaceBetween: 16,
        slidesPerGroup: 1,
      },
      768: {
        slidesPerView: "auto",
        spaceBetween: 24,
        slidesPerGroup: 1,
      },
      1024: {
        slidesPerView: 3,
        navigation: true,
        spaceBetween: 24,
        slidesPerGroup: 2,
      },
      1280: {
        slidesPerView: 3,
        navigation: true,
        spaceBetween: 24,
        slidesPerGroup: 2,
      },
      1440: {
        slidesPerView: 3,
        navigation: true,
        spaceBetween: 24,
        slidesPerGroup: 2,
      },
      1536: {
        slidesPerView: "auto",
        navigation: true,
        spaceBetween: 24,
        slidesPerGroup: 2,
      },
    },
    on: {
      slideChange: () => {
        if (swiperRetailersEl.swiper.isBeginning) {
          buttonRetailersPrevEl.classList.add("hidden");
        } else {
          buttonRetailersPrevEl.classList.remove("hidden");
        }

        if (swiperRetailersEl.swiper.isEnd) {
          buttonRetailersNextEl.classList.add("hidden");
        } else {
          buttonRetailersNextEl.classList.remove("hidden");
        }

        if (swiperProductsEl.swiper.isBeginning) {
          buttonProductsPrevEl.classList.add("hidden");
        } else {
          buttonProductsPrevEl.classList.remove("hidden");
        }

        if (swiperProductsEl.swiper.isEnd) {
          buttonProductsNextEl.classList.add("hidden");
        } else {
          buttonProductsNextEl.classList.remove("hidden");
        }
      },
    },
  };

  var container = document.getElementById("container");
  var containerComputedStyle = window.getComputedStyle(container);

  const swiperRetailersEl =
    containerComputedStyle.display === "none"
      ? document.getElementById("retailers-slider-mobile")
      : document.getElementById("retailers-slider");
  const buttonRetailersPrevEl =
    containerComputedStyle.display === "none"
      ? document.getElementById("prev-button-retailers-mobile")
      : document.getElementById("prev-button-retailers");
  const buttonRetailersNextEl =
    containerComputedStyle.display === "none"
      ? document.getElementById("next-button-retailers-mobile")
      : document.getElementById("next-button-retailers");

  buttonRetailersPrevEl.addEventListener("click", () => {
    swiperRetailersEl.swiper.slidePrev();
  });

  buttonRetailersNextEl.addEventListener("click", () => {
    swiperRetailersEl.swiper.slideNext();
  });

  // now we need to assign all parameters to Swiper element
  Object.assign(swiperRetailersEl, swiperParams);

  // and now initialize it

  swiperRetailersEl.initialize();

  const swiperProductsEl =
    containerComputedStyle.display === "none"
      ? document.getElementById("products-slider-mobile")
      : document.getElementById("products-slider");
  const buttonProductsPrevEl =
    containerComputedStyle.display === "none"
      ? document.getElementById("prev-button-products-mobile")
      : document.getElementById("prev-button-products");
  const buttonProductsNextEl =
    containerComputedStyle.display === "none"
      ? document.getElementById("next-button-products-mobile")
      : document.getElementById("next-button-products");

  buttonProductsPrevEl.addEventListener("click", () => {
    swiperProductsEl.swiper.slidePrev();
  });

  buttonProductsNextEl.addEventListener("click", () => {
    swiperProductsEl.swiper.slideNext();
  });

  // now we need to assign all parameters to Swiper element

  Object.assign(swiperProductsEl, swiperParams);

  // and now initialize it

  swiperProductsEl.initialize();
}

window.addEventListener("load", sliders);
window.addEventListener("resize", sliders);
