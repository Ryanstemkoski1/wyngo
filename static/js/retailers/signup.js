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
const name = document.querySelectorAll('[name="name"]');
const terms_conditions = document.querySelectorAll('[name="terms_conditions"]');
const description = document.querySelectorAll('[name="description"]');
const image = document.querySelectorAll('[name="image"]');
const category = document.querySelectorAll('[name="category"]');
const formats = document.querySelectorAll('[name="formats"]');
const button = document.querySelector("button");
const password = document.querySelectorAll('[name="password"]');

let isValidEmail = false;
let isValidPassword = false;
let isValidName = false;
let isValidTermsConditions = false;
let isValidDescription = false;
let isValidCategory = false;
let isValidImage = false;
let can_continue = document.querySelector('[name="continue"]').value;

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

const validate = () => {
  if (isValidName && isValidEmail &&
        isValidPassword &&
        terms_conditions[0].checked &&
        isValidCategory &&
        isValidDescription &&
        isValidImage &&
        can_continue !== "False") {
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

  validate();
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

  validate();
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

  validate();
});

email[0].addEventListener("keypress", function (event) {
  if (event.key === " " || event.keyCode === 32) {
    event.preventDefault();
  }
});

description[0].addEventListener("keyup", function () {
  let value = this.value;
  let length = value.length;

  if (value.startsWith(" ")) {
    this.value = "";
    isValidDescription = false;
    return;
  }

  if (length >= 1 && length <= 300) {
    isValidDescription = true;
    this.classList.remove("input__error");
    this.nextElementSibling.classList.add("hidden");
    this.nextElementSibling.nextElementSibling.classList.add("hidden");
  } else if (length < 1) {
    isValidDescription = false;
    this.classList.add("input__error");
    this.nextElementSibling.classList.remove("hidden");
    this.nextElementSibling.nextElementSibling.classList.add("hidden");
  } else {
    isValidDescription = false;
    this.classList.add("input__error");
    this.nextElementSibling.classList.add("hidden");
    this.nextElementSibling.nextElementSibling.classList.remove("hidden");
  }

  validate();
});

category[0].addEventListener("change", function () {
  let value = this.value;
  let length = value.length;

  if (length < 1) {
    isValidCategory = false;
    this.classList.add("input__error");
    this.classList.add("text-neutral-400");
  } else {
    isValidCategory = true;
    this.classList.remove("input__error");
    this.classList.remove("text-neutral-400");
  }

  validate();
});

image[0].addEventListener("change", function () {
  let file = this.files[0];

  if (file && /.(gif|jpeg|jpg|png)$/i.test(file.name)) {
    isValidImage = true;
    this.classList.remove("text-neutral-400");
    this.parentNode.classList.remove("input__error");
    formats[0].classList.add("hidden");
  } else {
    isValidImage = false;
    formats[0].classList.remove("hidden");
    this.classList.add("text-neutral-400");
    this.parentNode.classList.add("input__error");
  }

  validate();
});

terms_conditions[0].addEventListener("change", function () {
  validate();
});

const closeAlert = document.querySelector(".close-alert");

if (closeAlert) {
  closeAlert.addEventListener("click", function () {
    this.parentNode.parentNode.classList.add("hidden");
  });
}
