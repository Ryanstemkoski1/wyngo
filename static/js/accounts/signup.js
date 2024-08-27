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
const confirm_password = document.querySelectorAll('[name="confirm_password"]');
const name = document.querySelectorAll('[name="name"]');
const last_name = document.querySelectorAll('[name="last_name"]');
const terms_conditions = document.querySelectorAll('[name="terms_conditions"]');
const button = document.querySelector("button");

let isValidEmail = false;
let isValidPassword = false;
let isValidConfirmPassword = false;
let isValidName = false;
let isValidLastName = false;
let isValidTermsConditions = false;

email.forEach((input) => {
  input.addEventListener("keyup", () => {
    const value = input.value;
    if (validator.isEmail(value)) {
      document.querySelector(".envelope-icon").src = emailIcon.valid;
    } else {
      document.querySelector(".envelope-icon").src = emailIcon.invalid;
    }
  });
});

const validate = (
  isValidName,
  isValidLastName,
  isValidEmail,
  isValidPassword,
  isValidConfirmPassword
) => {
  if (
    isValidName &&
    isValidLastName &&
    isValidEmail &&
    isValidPassword &&
    isValidConfirmPassword &&
    terms_conditions[0].checked
  ) {
    button.disabled = false;
  } else {
    button.disabled = true;
  }
};

name[0].addEventListener("keyup", function () {
  let value = this.value;
  let length = value.length;

  if (value.startsWith(" ")) {
    this.value = "";
    isValidName = false;
    return;
  }

  if (length >= 1 && length <= 36) {
    isValidName = true;
    this.classList.remove("input__error");
    this.nextElementSibling.classList.add("hidden");
    this.nextElementSibling.nextElementSibling.classList.add("hidden");
  } else if (length < 1) {
    isValidName = false;
    this.classList.add("input__error");
    this.nextElementSibling.classList.remove("hidden");
    this.nextElementSibling.nextElementSibling.classList.add("hidden");
  } else {
    isValidName = false;
    this.classList.add("input__error");
    this.nextElementSibling.classList.add("hidden");
    this.nextElementSibling.nextElementSibling.classList.remove("hidden");
  }

  validate(
    isValidName,
    isValidLastName,
    isValidEmail,
    isValidPassword,
    isValidConfirmPassword
  );
});

last_name[0].addEventListener("keyup", function () {
  let value = this.value;
  let length = value.length;

  if (value.startsWith(" ")) {
    this.value = "";
    isValidName = false;
    return;
  }

  if (length >= 1 && length <= 36) {
    isValidLastName = true;
    this.classList.remove("input__error");
    this.nextElementSibling.classList.add("hidden");
    this.nextElementSibling.nextElementSibling.classList.add("hidden");
  } else if (length < 1) {
    isValidLastName = false;
    this.classList.add("input__error");
    this.nextElementSibling.classList.remove("hidden");
    this.nextElementSibling.nextElementSibling.classList.add("hidden");
  } else {
    isValidLastName = false;
    this.classList.add("input__error");
    this.nextElementSibling.classList.add("hidden");
    this.nextElementSibling.nextElementSibling.classList.remove("hidden");
  }

  validate(
    isValidName,
    isValidLastName,
    isValidEmail,
    isValidPassword,
    isValidConfirmPassword
  );
});

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

  validate(
    isValidName,
    isValidLastName,
    isValidEmail,
    isValidPassword,
    isValidConfirmPassword
  );
});

email[0].addEventListener("keypress", function (event) {
  if (event.key === " " || event.keyCode === 32) {
    event.preventDefault();
  }
});

password[0].addEventListener("keyup", function () {
  let value = this.value;

  if (value.startsWith(" ")) {
    this.value = "";
    isValidName = false;
    return;
  }

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

  if (confirm_password[0].value !== "" && !validator.equals(this.value, confirm_password[0].value)) {
    isValidConfirmPassword = false;
    confirm_password[0].classList.add("input__error");
    confirm_password[0].parentNode.nextElementSibling.classList.remove("hidden");
  } else if(validator.equals(this.value, confirm_password[0].value)) {
    isValidConfirmPassword = true;
    confirm_password[0].classList.remove("input__error");
    confirm_password[0].parentNode.nextElementSibling.classList.add("hidden");
  }

  validate(
    isValidName,
    isValidLastName,
    isValidEmail,
    isValidPassword,
    isValidConfirmPassword
  );
});

password[0].addEventListener("keypress", function (event) {
  if (event.key === " " || event.keyCode === 32) {
    event.preventDefault();
  }
});

confirm_password[0].addEventListener("keyup", function () {
  let value = this.value;

  if (value.startsWith(" ")) {
    this.value = "";
    isValidName = false;
    return;
  }

  if (validator.equals(this.value, password[0].value)) {
    isValidConfirmPassword = true;
    this.classList.remove("input__error");
    this.parentNode.nextElementSibling.classList.add("hidden");
  } else {
    isValidConfirmPassword = false;
    this.classList.add("input__error");
    this.parentNode.nextElementSibling.classList.remove("hidden");
  }

  validate(
    isValidName,
    isValidLastName,
    isValidEmail,
    isValidPassword,
    isValidConfirmPassword
  );
});

confirm_password[0].addEventListener("keypress", function (event) {
  if (event.key === " " || event.keyCode === 32) {
    event.preventDefault();
  }
});

terms_conditions[0].addEventListener("change", function () {
  validate(
    isValidName,
    isValidLastName,
    isValidEmail,
    isValidPassword,
    isValidConfirmPassword
  );
});

const closeAlert = document.querySelector(".close-alert");

if (closeAlert) {
  closeAlert.addEventListener("click", function () {
    this.parentNode.parentNode.classList.add("hidden");
  });
}
