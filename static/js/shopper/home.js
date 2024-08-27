function getID(element) {
  id = element.getAttribute("id").split("_")[1];
  return id;
}

function favoriteBtn(element) {
  const favoriteID = getID(element);
  const favoriteIcon = document.getElementById(`favorite_${favoriteID}`);
  favoriteIcon.classList.toggle("fill-white");
}

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

function editBtn(element) {
  id = getID(element);
  const editBtn = document.getElementById(`edit_${id}`);

  const saveBtn = document.getElementById(`save_${id}`);

  const quantity = document.getElementById(`quantity_${id}`).value;

  document.getElementById(`plus_${id}`).removeAttribute("disabled");

  if (quantity > 1) {
    document.getElementById(`minus_${id}`).removeAttribute("disabled");
  }

  editBtn.classList.toggle("hidden");

  saveBtn.classList.toggle("hidden");
}

function cancelBtn(element) {
  id = getID(element);

  const modal = document.getElementById(`cancel_modal_${id}`);

  modal.showModal();
}

function closeModal(element) {
  id = getID(element);

  const modal = document.getElementById(`cancel_modal_${id}`);

  modal.close();
}

/* Near You Slider */
let swiperNearYouEl;
let swiperJustAddedEl;
let swiperRetailersEl;
let swiperUpcomingEl;

commonParams = {
  loop: false,
  spaceBetween: 16,
  slidesPerView: 1.5,
  slidesPerGroup: 2,
  breakpoints: {
    320: {
      slidesPerGroup: 1,
    },
    375: {
      slidesPerView: "auto",
      spaceBetween: 16,
      slidesPerGroup: 1,
    },
    768: {
      slidesPerView: "auto",
      spaceBetween: 24,
      slidesPerGroup: 2,
    },
    1024: {
      slidesPerView: 3,
      navigation: true,
      spaceBetween: 24,
      slidesPerGroup: 3,
    },
    1280: {
      slidesPerView: 4,
      navigation: true,
      spaceBetween: 24,
      slidesPerGroup: 4,
    },
    1440: {
      slidesPerView: 4,
      navigation: true,
      spaceBetween: 24,
      slidesPerGroup: 4,
    },
    1536: {
      slidesPerView: "auto",
      navigation: true,
      spaceBetween: 24,
      slidesPerGroup: 4,
    },
  },
};

// swiper parameters
const swiperParamsUpcomingReservations = {
  ...commonParams,
  on: {
    slideChange: () => {
      if (swiperUpcomingEl) {
        if (swiperUpcomingEl.swiper.isBeginning) {
          buttonUpcomingPrevEl.classList.add("hidden");
        } else {
          buttonUpcomingPrevEl.classList.remove("hidden");
        }

        if (swiperUpcomingEl.swiper.isEnd) {
          buttonUpcomingNextEl.classList.add("hidden");
        } else {
          buttonUpcomingNextEl.classList.remove("hidden");
        }
      }
    },
    init: () => {
      if (swiperUpcomingEl && swiperUpcomingEl.swiper) {
        if (swiperUpcomingEl.swiper.isEnd) {
          buttonUpcomingNextEl.classList.add("hidden");
        } else {
          buttonUpcomingNextEl.classList.remove("hidden");
        }
      }
    },
  },
};

const swiperParamsNearYou = {
  ...commonParams,
  on: {
    slideChange: () => {
      if (swiperNearYouEl.swiper.isBeginning) {
        buttonNearYouPrevEl.classList.add("hidden");
      } else {
        buttonNearYouPrevEl.classList.remove("hidden");
      }

      if (swiperNearYouEl.swiper.isEnd) {
        buttonNearYouNextEl.classList.add("hidden");
      } else {
        buttonNearYouNextEl.classList.remove("hidden");
      }
    },
    init: () => {
      if (swiperNearYouEl && swiperNearYouEl.swiper) {
        if (swiperNearYouEl.swiper.isEnd) {
          buttonNearYouNextEl.classList.add("hidden");
        } else {
          buttonNearYouNextEl.classList.remove("hidden");
        }
      }
    },
  },
};

const swiperParamsJustAdded = {
  ...commonParams,
  on: {
    slideChange: () => {
      if (swiperJustAddedEl.swiper.isBeginning) {
        buttonJustAddedPrevEl.classList.add("hidden");
      } else {
        buttonJustAddedPrevEl.classList.remove("hidden");
      }

      if (swiperJustAddedEl.swiper.isEnd) {
        buttonJustAddedNextEl.classList.add("hidden");
      } else {
        buttonJustAddedNextEl.classList.remove("hidden");
      }
    },
    init: () => {
      if (swiperJustAddedEl && swiperJustAddedEl.swiper) {
        if (swiperJustAddedEl.swiper.isEnd) {
          buttonJustAddedNextEl.classList.add("hidden");
        } else {
          buttonJustAddedNextEl.classList.remove("hidden");
        }
      }
    },
  },
};

const swiperParamsRetailers = {
  ...commonParams,
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
    },
    init: () => {
      if (swiperRetailersEl && swiperRetailersEl.swiper) {
        if (swiperRetailersEl.swiper.isEnd) {
          buttonRetailersNextEl.classList.add("hidden");
        } else {
          buttonRetailersNextEl.classList.remove("hidden");
        }
      }
    },
  },
};

// swiper element
swiperNearYouEl = document.getElementById("near-you-slider");
const buttonNearYouPrevEl = document.getElementById("prev-button-near-you");
const buttonNearYouNextEl = document.getElementById("next-button-near-you");

buttonNearYouPrevEl.addEventListener("click", () => {
  swiperNearYouEl.swiper.slidePrev();
});

buttonNearYouNextEl.addEventListener("click", () => {
  swiperNearYouEl.swiper.slideNext();
});

// now we need to assign all parameters to Swiper element
Object.assign(swiperNearYouEl, swiperParamsNearYou);

// and now initialize it
swiperNearYouEl.initialize();

/* Just Added Slider */

// swiper element
swiperJustAddedEl = document.getElementById("just-added-slider");
const buttonJustAddedPrevEl = document.getElementById("prev-button-just-added");
const buttonJustAddedNextEl = document.getElementById("next-button-just-added");

buttonJustAddedPrevEl.addEventListener("click", () => {
  swiperJustAddedEl.swiper.slidePrev();
});

buttonJustAddedNextEl.addEventListener("click", () => {
  swiperJustAddedEl.swiper.slideNext();
});

// now we need to assign all parameters to Swiper element
Object.assign(swiperJustAddedEl, swiperParamsJustAdded);

// and now initialize it

swiperJustAddedEl.initialize();

/* Retailers Slider */

swiperRetailersEl = document.getElementById("retailers-slider");
const buttonRetailersPrevEl = document.getElementById("prev-button-retailers");
const buttonRetailersNextEl = document.getElementById("next-button-retailers");

buttonRetailersPrevEl.addEventListener("click", () => {
  swiperRetailersEl.swiper.slidePrev();
});

buttonRetailersNextEl.addEventListener("click", () => {
  swiperRetailersEl.swiper.slideNext();
});

// now we need to assign all parameters to Swiper element
Object.assign(swiperRetailersEl, swiperParamsRetailers);

// and now initialize it

swiperRetailersEl.initialize();

/* Upcoming reservations slider */

swiperUpcomingEl = document.getElementById("upcoming-slider");
const buttonUpcomingPrevEl = document.getElementById("prev-button-upcoming");

const buttonUpcomingNextEl = document.getElementById("next-button-upcoming");

document.addEventListener("DOMContentLoaded", () => {
  if (swiperUpcomingEl) {
    buttonUpcomingPrevEl.addEventListener("click", () => {
      swiperUpcomingEl.swiper.slidePrev();
    });

    buttonUpcomingNextEl.addEventListener("click", () => {
      swiperUpcomingEl.swiper.slideNext();
    });

    // now we need to assign all parameters to Swiper element
    Object.assign(swiperUpcomingEl, swiperParamsUpcomingReservations);

    // and now initialize it

    swiperUpcomingEl.initialize();
  }
});

const closeAlert = document.querySelector(".close-alert");

if (closeAlert) {
  closeAlert.addEventListener("click", function () {
    this.parentNode.parentNode.classList.add("hidden");
  });
}

function reserveBtn(element) {
  id = getID(element);

  const form = document.getElementById(`make-res_${id}`);

  form.submit();

  const reserveBtn = document.getElementById(`reserve_${id}`);

  reserveBtn.setAttribute("disabled", "disabled");
  reserveBtn.classList.add("opacity-50");
}
