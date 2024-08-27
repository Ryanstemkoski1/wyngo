const email = document.querySelectorAll('[name="email"]');
const button = document.querySelector("button");

let isValidEmail = false;

const validate = (isValidEmail) => {
  if (isValidEmail) {
    button.disabled = false;
  } else {
    button.disabled = true;
  }
};

email[0].addEventListener("keyup", function () {
  if (validator.isEmail(this.value)) {
    isValidEmail = true;
    this.classList.remove("input__error");
    this.parentNode.nextElementSibling.classList.add("hidden");
  } else {
    isValidEmail = false;
    this.classList.add("input__error");
    this.parentNode.nextElementSibling.classList.remove("hidden");
  }

  validate(isValidEmail);
});

const closeAlert = document.querySelector(".close-alert");

if (closeAlert) {
  closeAlert.addEventListener("click", function () {
    this.parentNode.parentNode.classList.add("hidden");
  });
}
