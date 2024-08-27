const arrow = document.querySelector(".arrow");
let toggle = false;

if (arrow) {
  arrow.addEventListener("click", function () {
    if (!toggle) {
      this.src = arrowIcon.up;
      this.parentNode.nextElementSibling.classList.remove("hidden");
      toggle = true;
    } else {
      this.src = arrowIcon.down;
      this.parentNode.nextElementSibling.classList.add("hidden");
      toggle = false;
    }
  });
}

const drawerCheckbox = document.querySelector(".drawer-toggle");
const closeDrawer = document.querySelector(".close-drawer");

if (closeDrawer) {
  closeDrawer.addEventListener("click", function () {
    drawerCheckbox.checked = false;
    document.body.style.overflow = "auto";
  });
}

if (drawerCheckbox) {
  drawerCheckbox.addEventListener("change", function () {
    if (this.checked) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
  });
}

const searchIcon = document.getElementById("searchIcon");
const closeIcon = document.getElementById("closeIcon");
const searchInput = document.getElementById("searchInputMobile");
const searchContainer = document.querySelector(".search-container");
const logo = document.querySelector(".brand");

if (searchIcon) {
  searchIcon.parentElement.addEventListener("click", () => {
    closeIcon.classList.toggle("hidden");
    searchInput.classList.toggle("hidden");
    searchInput.parentElement.classList.toggle("grow");
    searchInput.parentElement.parentElement.classList.toggle("grow");
    searchIcon.parentElement.classList.toggle("absolute");
    logo.classList.toggle("hidden");
    searchIcon.classList.toggle("hidden");
  });
}
