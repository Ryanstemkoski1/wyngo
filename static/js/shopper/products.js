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

// swiper element
const swiperProductGalleryEl = document.getElementById("product-gallery");
const buttonProductGalleryPrevEl = document.getElementById(
  "prev-button-product-gallery"
);
const buttonProductGalleryNextEl = document.getElementById(
  "next-button-product-gallery"
);

const closeAlert = document.querySelector(".close-alert");

if (closeAlert) {
  closeAlert.addEventListener("click", function () {
    this.parentNode.parentNode.classList.add("hidden");
  });
}

buttonProductGalleryPrevEl.addEventListener("click", () => {
  swiperProductGalleryEl.swiper.slidePrev();
});

buttonProductGalleryNextEl.addEventListener("click", () => {
  swiperProductGalleryEl.swiper.slideNext();
});

const swiperProductGalleryThumbsEl = document.getElementById(
  "product-gallery-thumbs"
);

function updateThumbOpacity(activeIndex) {
  const thumbs = document.querySelectorAll(".gallery-thumbs swiper-slide");
  thumbs.forEach((thumb, index) => {
    if (index === activeIndex) {
      thumb.style.opacity = 1;
    } else {
      thumb.style.opacity = 0.6; // Set the opacity for inactive thumbs
    }
  });
}

// swiper thumbs
Object.assign(swiperProductGalleryThumbsEl, {
  loop: false,
  spaceBetween: 8,
  autoHeight: true,
  calculateHeight: true,
  centerSlides: true,
  breakpoints: {
    320: {
      slidesPerView: "auto",
    },
    375: {
      slidesPerView: "auto",
    },
    768: {
      slidesPerView: "auto",
    },
    1024: {
      slidesPerView: "auto",
    },
    1280: {
      slidesPerView: "auto",
    },
    1440: {
      slidesPerView: "auto",
    },
    1536: {
      slidesPerView: "auto",
    },
  },
});

// now we need to initialize it
swiperProductGalleryThumbsEl.initialize();

// swiper parameters
const swiperGalleryParams = {
  loop: false,
  spaceBetween: 8,
  thumbs: {
    swiper: swiperProductGalleryThumbsEl.swiper,
  },
  breakpoints: {
    320: {},
    375: {},
    768: {},
    1024: {},
    1280: {},
    1440: {},
    1536: {},
  },
  on: {
    slideChange: () => {
      updateThumbOpacity(swiperProductGalleryEl.swiper.activeIndex);

      if (swiperProductGalleryEl.swiper.isBeginning) {
        buttonProductGalleryPrevEl.classList.add("opacity-50");
      } else {
        buttonProductGalleryPrevEl.classList.remove("opacity-50");
      }

      if (swiperProductGalleryEl.swiper.isEnd) {
        buttonProductGalleryNextEl.classList.add("opacity-50");
      } else {
        buttonProductGalleryNextEl.classList.remove("opacity-50");
      }
    },
    init: () => {
      if (swiperProductGalleryEl && swiperProductGalleryEl.swiper) {
        if (swiperProductGalleryEl.swiper.isEnd) {
          buttonProductGalleryNextEl.classList.add("opacity-50");
        } else {
          buttonProductGalleryNextEl.classList.remove("opacity-50");
        }
      }
    },
  },
};

// now we need to assign all parameters to Swiper element
Object.assign(swiperProductGalleryEl, swiperGalleryParams);

// and now initialize it
swiperProductGalleryEl.initialize();

function updateGallery(images) {
  swiperProductGalleryEl.swiper.removeAllSlides();
  swiperProductGalleryThumbsEl.swiper.removeAllSlides();

  images.forEach((image) => {
    swiperProductGalleryEl.swiper.appendSlide(
      `<swiper-slide class="flex justify-center">
      <img src="${image}" alt="Product image" class="h-full object-fill">
      </swiper-slide>`
    );

    swiperProductGalleryThumbsEl.swiper.appendSlide(
      `<swiper-slide class="rounded-xl border border-w-indigo w-16 h-16 lg:w-20 lg:h-20 flex justify-center">
      <img src="${image}" alt="Product image" class="h-full object-fill rounded-xl">
      </swiper-slide>`
    );
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const images = variantImages.filter((image) => image.id === currentVariant)[0]
    .images;

  if (images.length > 0) {
    updateGallery(images);
  } else {
    updateGallery([noImage]);
  }
});

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

function applyFilter() {
  const radio = document.querySelector('input[name="variation-radio"]:checked');
  const filter = radio.value;
  document.getElementById("variations_mobile").value = filter;
  document.getElementById("variation").value = filter;
  overlay.style.opacity = "0";
  drawer.style.height = "0";
  document.body.classList.remove("overflow-hidden");

  price = radio.getAttribute("data-price");
  product_name = radio.getAttribute("data-name");
  stock = parseInt(radio.getAttribute("data-stock"));

  document.getElementById("price").innerHTML = `$${price}`;
  document.getElementById("product_name").innerHTML = product_name;
  document.getElementById("product_name_2").innerHTML = product_name;

  const score = document.getElementById("score")

  if (stock < 1) {
    score.value = 33;
    score.classList.remove("progress-bar-danger", "progress-bar-warning", "progress-bar-success");
    score.classList.add(`progress-bar-danger`);
  } else if (stock === 1) {
    score.value = 66;
    score.classList.remove("progress-bar-danger", "progress-bar-warning", "progress-bar-success");
    score.classList.add(`progress-bar-warning`);
  } else {
    score.value = 100;
    score.classList.remove("progress-bar-danger", "progress-bar-warning", "progress-bar-success");
    score.classList.add(`progress-bar-success`);
  }

  const images = variantImages.filter(
    (image) => image.id === parseInt(filter)
  )[0].images;

  if (images.length > 0) {
    updateGallery(images);
  } else {
    updateGallery([noImage]);
  }
}

let swiperRelatedItemsEl;

const swiperParams = {
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
  on: {
    slideChange: () => {
      if (swiperRelatedItemsEl.swiper.isBeginning) {
        buttonRelatedItemsPrevEl.classList.add("hidden");
      } else {
        buttonRelatedItemsPrevEl.classList.remove("hidden");
      }

      if (swiperRelatedItemsEl.swiper.isEnd) {
        buttonRelatedItemsNextEl.classList.add("hidden");
      } else {
        buttonRelatedItemsNextEl.classList.remove("hidden");
      }
    },
    init: () => {
      requestAnimationFrame(() => {
        if (swiperRelatedItemsEl?.swiper) {
          buttonRelatedItemsNextEl.classList.toggle(
            "hidden",
            swiperRelatedItemsEl.swiper.isEnd
          );
        }
      });
    },
  },
};

// swiper element
swiperRelatedItemsEl = document.getElementById("related-items-slider");
const buttonRelatedItemsPrevEl = document.getElementById(
  "prev-button-related-items"
);
const buttonRelatedItemsNextEl = document.getElementById(
  "next-button-related-items"
);

if (buttonRelatedItemsPrevEl) {
  buttonRelatedItemsPrevEl.addEventListener("click", () => {
    swiperRelatedItemsEl.swiper.slidePrev();
  });
}

if (buttonRelatedItemsNextEl) {
  buttonRelatedItemsNextEl.addEventListener("click", () => {
    swiperRelatedItemsEl.swiper.slideNext();
  });
}

  // now we need to assign all parameters to Swiper element
if (swiperRelatedItemsEl) {
  Object.assign(swiperRelatedItemsEl, swiperParams);

  // and now initialize it
  swiperRelatedItemsEl.initialize();
}

/* Custom select */

addEventListener("DOMContentLoaded", () => {
  var x, i, j, l, ll, selElmnt, a, b, c;
  /* Look for any elements with the class "custom-select": */
  x = document.getElementsByClassName("custom-select");
  l = x.length;

  for (i = 0; i < l; i++) {
    selElmnt = x[i].getElementsByTagName("select")[0];
    ll = selElmnt.length;
    /* For each element, create a new DIV that will act as the selected item: */
    a = document.createElement("DIV");
    a.setAttribute("class", "select-selected");
    a.setAttribute("id", "select-selected");
    a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
    x[i].appendChild(a);
    /* For each element, create a new DIV that will contain the option list: */
    b = document.createElement("DIV");

    if (ll > 5) {
      b.setAttribute("class", "select-items select-hide");
    } else {
      b.setAttribute("class", "select-items select-items-small select-hide");
    }

    b.setAttribute("id", "select-items");
    for (j = 0; j < ll; j++) {
      /* For each option in the original select element,
    create a new DIV that will act as an option item: */
      c = document.createElement("DIV");
      c.setAttribute("class", "div-item");
      c.innerHTML = selElmnt.options[j].innerHTML;
      if (j == selElmnt.selectedIndex) {
        c.setAttribute("class", "same-as-selected");
      }
      c.addEventListener("click", function (e) {
        /* When an item is clicked, update the original select box,
        and the selected item: */
        var y, i, k, s, h, sl, yl;
        s = this.parentNode.parentNode.getElementsByTagName("select")[0];
        sl = s.length;
        h = this.parentNode.previousSibling;
        for (i = 0; i < sl; i++) {
          if (s.options[i].innerHTML == this.innerHTML) {
            s.selectedIndex = i;
            price = s.options[i].getAttribute("data-price");
            product_name = s.options[i].getAttribute("data-name");
            stock = parseFloat(s.options[i].getAttribute("data-stock"));
            description = s.options[i].getAttribute("data-description");

            currentVariant = parseInt(s.options[i].value);

            const images = variantImages.filter(
              (image) => image.id === currentVariant
            )[0].images;

            if (images.length > 0) {
              updateGallery(images);
            } else {
              updateGallery([noImage]);
            }

            document.getElementById("price").innerHTML = `$${price}`;
            document.getElementById("product_name").innerHTML = product_name;
            document.getElementById("product_name_2").innerHTML = product_name;
            if (description) {
              document.getElementById("description").innerHTML = description;
            }

            const score = document.getElementById("score")

            if (stock < 1) {
              score.value = 33;
              score.classList.remove("progress-bar-danger", "progress-bar-warning", "progress-bar-success");
              score.classList.add(`progress-bar-danger`);
            } else if (stock === 1) {
              score.value = 66;
              score.classList.remove("progress-bar-danger", "progress-bar-warning", "progress-bar-success");
              score.classList.add(`progress-bar-warning`);
            } else {
              score.value = 100;
              score.classList.remove("progress-bar-danger", "progress-bar-warning", "progress-bar-success");
              score.classList.add(`progress-bar-success`);
            }

            h.innerHTML = this.innerHTML;
            y = this.parentNode.getElementsByClassName("same-as-selected");
            yl = y.length;
            for (k = 0; k < yl; k++) {
              y[k].setAttribute("class", "div-item");
            }
            this.setAttribute("class", "same-as-selected");
            break;
          }
        }
        h.click();
      });
      b.appendChild(c);
    }
    x[i].appendChild(b);
    a.addEventListener("click", function (e) {
      /* When the select box is clicked, close any other select boxes,
    and open/close the current select box: */
      e.stopPropagation();
      closeAllSelect(this);
      this.nextSibling.classList.toggle("select-hide");
      this.classList.toggle("select-arrow-active");
    });
  }

  function closeAllSelect(elmnt) {
    /* A function that will close all select boxes in the document,
  except the current select box: */
    var x,
      y,
      i,
      xl,
      yl,
      arrNo = [];
    x = document.getElementsByClassName("select-items");
    y = document.getElementsByClassName("select-selected");
    xl = x.length;
    yl = y.length;
    for (i = 0; i < yl; i++) {
      if (elmnt == y[i]) {
        arrNo.push(i);
      } else {
        y[i].classList.remove("select-arrow-active");
      }
    }
    for (i = 0; i < xl; i++) {
      if (arrNo.indexOf(i)) {
        x[i].classList.add("select-hide");
      }
    }
  }

  /* If the user clicks anywhere outside the select box,
then close all select boxes: */
  document.addEventListener("click", closeAllSelect);
});

function reserveBtn(element) {
  id = getID(element);

  const form = document.getElementById(`make-res_${id}`);

  form.submit();

  const reserveBtn = document.getElementById(`reserve_${id}`);

  reserveBtn.setAttribute("disabled", "disabled");
  reserveBtn.classList.add("opacity-50");
}
