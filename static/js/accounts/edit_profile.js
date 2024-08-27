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

const password = document.querySelectorAll('[name="password"]');
const confirm_password = document.querySelectorAll('[name="confirm_password"]');
const first_name = document.querySelectorAll('[name="first_name"]');
const last_name = document.querySelectorAll('[name="last_name"]');
const button = document.querySelector(".save");

let isValidName = true;
let isValidLastName = true;
let isValidPassword = true;
let isValidConfirmPassword = true;
let hasMinLength = false;
let hasUpperCase = false;
let hasLowerCase = false;
let hasNumber = false;

const validate = (
  isValidName,
  isValidLastName,
  isValidPassword,
  isValidConfirmPassword
) => {
  if (
    isValidName &&
    isValidLastName &&
    isValidPassword &&
    isValidConfirmPassword
  ) {
    console.log("valid");
    button.disabled = false;
  } else {
    console.log("invalid");
    button.disabled = true;
  }
};

first_name[0].addEventListener("keyup", function () {
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
    isValidPassword,
    isValidConfirmPassword
  );
});

const checkPassword = (password, confirm_password) => {
  if (!password && !confirm_password) {
    isValidPassword = true;
    isValidConfirmPassword = true;
    document
      .querySelector(".check-min")
      .classList.remove("text-w-primary", "material-icons");
    document
      .querySelector(".check-min")
      .classList.add("material-icons-outlined");

    document
      .querySelector(".check-upper")
      .classList.remove("text-w-primary", "material-icons");

    document
      .querySelector(".check-upper")
      .classList.add("material-icons-outlined");

    document
      .querySelector(".check-lower")
      .classList.remove("text-w-primary", "material-icons");

    document
      .querySelector(".check-number")
      .classList.remove("text-w-primary", "material-icons");
    document
      .querySelector(".check-number")
      .classList.add("material-icons-outlined");

    document
      .querySelector(".check-match")
      .classList.remove("text-w-primary", "material-icons");
    document
      .querySelector(".check-match")
      .classList.add("material-icons-outlined");
  }
};

password[0].addEventListener("keyup", function () {
  isValidConfirmPassword = false;
  if (validator.isLength(this.value, { min: 8 })) {
    hasMinLength = true;
    document
      .querySelector(".check-min")
      .classList.add("material-icons", "text-w-primary");
  } else {
    hasMinLength = false;
    document
      .querySelector(".check-min")
      .classList.remove("text-w-primary", "material-icons");
    document
      .querySelector(".check-min")
      .classList.add("material-icons-outlined");
  }

  if (this.value.match(/\p{Lu}/u)) {
    hasUpperCase = true;
    document
      .querySelector(".check-upper")
      .classList.add("material-icons", "text-w-primary");
  } else {
    hasUpperCase = false;
    document
      .querySelector(".check-upper")
      .classList.remove("text-w-primary", "material-icons");
    document
      .querySelector(".check-upper")
      .classList.add("material-icons-outlined");
  }

  if (this.value.match(/\p{Ll}/u)) {
    hasLowerCase = true;
    document
      .querySelector(".check-lower")
      .classList.add("material-icons", "text-w-primary");
  } else {
    hasLowerCase = false;
    document
      .querySelector(".check-lower")
      .classList.remove("text-w-primary", "material-icons");
    document
      .querySelector(".check-lower")
      .classList.add("material-icons-outlined");
  }

  if (this.value.match(/\p{N}/u)) {
    hasNumber = true;
    document
      .querySelector(".check-number")
      .classList.add("material-icons", "text-w-primary");
  } else {
    hasNumber = false;
    document
      .querySelector(".check-number")
      .classList.remove("text-w-primary", "material-icons");
    document
      .querySelector(".check-number")
      .classList.add("material-icons-outlined");
  }

  if (
    validator.equals(this.value, confirm_password[0].value) &&
    hasMinLength &&
    hasUpperCase &&
    hasLowerCase &&
    hasNumber
  ) {
    isValidPassword = true;
    isValidConfirmPassword = true;
    document
      .querySelector(".check-match")
      .classList.add("material-icons", "text-w-primary");
  } else {
    isValidPassword = false;
    isValidConfirmPassword = false;
    document
      .querySelector(".check-match")
      .classList.remove("text-w-primary", "material-icons");
    document
      .querySelector(".check-match")
      .classList.add("material-icons-outlined");
  }

  checkPassword(this.value, confirm_password[0].value);

  validate(
    isValidName,
    isValidLastName,
    isValidPassword,
    isValidConfirmPassword
  );
});

confirm_password[0].addEventListener("keyup", function () {
  if (
    validator.equals(this.value, password[0].value) &&
    hasMinLength &&
    hasUpperCase &&
    hasLowerCase &&
    hasNumber
  ) {
    isValidPassword = true;
    isValidConfirmPassword = true;
    document
      .querySelector(".check-match")
      .classList.add("material-icons", "text-w-primary");
  } else {
    isValidPassword = false;
    isValidConfirmPassword = false;
    document
      .querySelector(".check-match")
      .classList.remove("text-w-primary", "material-icons");
    document
      .querySelector(".check-match")
      .classList.add("material-icons-outlined");
  }

  checkPassword(password[0].value, this.value);

  validate(
    isValidName,
    isValidLastName,
    isValidPassword,
    isValidConfirmPassword
  );
});

const editBtn = document.querySelector(".edit-btn");
const cancelBtn = document.querySelector(".cancel-btn");

editBtn.addEventListener("click", function (e) {
  document.querySelector(".actions").classList.remove("hidden");
  first_name[0].removeAttribute("disabled");
  last_name[0].removeAttribute("disabled");
  password[0].removeAttribute("disabled");
  confirm_password[0].removeAttribute("disabled");
});

cancelBtn.addEventListener("click", function (e) {
  document.querySelector(".actions").classList.add("hidden");
  first_name[0].setAttribute("disabled", true);
  last_name[0].setAttribute("disabled", true);
  password[0].setAttribute("disabled", true);
  confirm_password[0].setAttribute("disabled", true);
});

const closeAlert = document.querySelector(".close-alert");

if (closeAlert) {
  closeAlert.addEventListener("click", function () {
    this.parentNode.parentNode.parentNode.classList.add("hidden");
  });
}

password[0].addEventListener("keypress", function (event) {
  if (event.key === " " || event.keyCode === 32) {
    event.preventDefault();
  }
});

confirm_password[0].addEventListener("keypress", function (event) {
  if (event.key === " " || event.keyCode === 32) {
    event.preventDefault();
  }
});
