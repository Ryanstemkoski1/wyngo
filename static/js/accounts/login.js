const eye = document.querySelectorAll(".eye-icon");

eye.forEach((eye) => {
  eye.addEventListener("click", () => {
    const input = eye.previousElementSibling;
    if (input.type === "password") {
      input.type = "text";
      eye.src = showPasswordIcon.show;
    } else {
      input.type = "password";
      eye.src = showPasswordIcon.hide;
    }
  });
});
const email = document.querySelectorAll('[name="email"]');
const password = document.querySelectorAll('[name="password"]');
const button = document.querySelector("button");

let isValidEmail = false;
let isValidPassword = false;

const validate = (isValidEmail, isValidPassword) => {
  if (isValidEmail && isValidPassword) {
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

  validate(isValidEmail, isValidPassword);
});

password[0].addEventListener("keyup", function () {
  if (
    validator.isStrongPassword(this.value, {
      minLength: 8,
      minLowercase: 1,
      minUppercase: 1,
      minNumbers: 1,
      minSymbols: 0,
    })
  ) {
    isValidPassword = true;
    this.classList.remove("input__error");
    this.parentNode.nextElementSibling.classList.add("hidden");
  } else {
    isValidPassword = false;
    this.classList.add("input__error");
    this.parentNode.nextElementSibling.classList.remove("hidden");
  }

  validate(isValidEmail, isValidPassword);
});

password[0].addEventListener("keypress", function (event) {
  if (event.key === " " || event.keyCode === 32) {
    event.preventDefault();
  }
});

const closeAlert = document.querySelector(".close-alert");

if (closeAlert) {
  closeAlert.addEventListener("click", function () {
    this.parentNode.parentNode.classList.add("hidden");
  });
}
