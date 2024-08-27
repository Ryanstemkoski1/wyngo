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

const password = document.querySelector('[name="new_password1"]');
const confirm_password = document.querySelector('[name="new_password2"]');
const button = document.querySelector("button");

let isValidPassword = false;
let isValidConfirmPassword = false;

const validate = (isValidPassword, isValidConfirmPassword) => {
  if (isValidPassword && isValidConfirmPassword) {
    button.disabled = false;
  } else {
    button.disabled = true;
  }
};

password.addEventListener("keyup", function () {
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

  if (confirm_password.value !== "" && !validator.equals(this.value, confirm_password.value)) {
    isValidConfirmPassword = false;
    confirm_password.classList.add("input__error");
    confirm_password.parentNode.nextElementSibling.classList.remove("hidden");
  } else if(validator.equals(this.value, confirm_password.value)){
    isValidConfirmPassword = true;
    confirm_password.classList.remove("input__error");
    confirm_password.parentNode.nextElementSibling.classList.add("hidden");
  }

  validate(isValidPassword, isValidConfirmPassword);
});

confirm_password.addEventListener("keyup", function () {
    if (validator.equals(this.value, password.value)) {
        if (
            validator.isStrongPassword(this.value, {
                minLength: 8,
                minLowercase: 1,
                minUppercase: 1,
                minNumbers: 1,
                minSymbols: 0,
            })
        ) {
            isValidConfirmPassword = true;
            this.classList.remove("input__error");
            this.parentNode.nextElementSibling.classList.add("hidden");
        }else if (this.value === password.value){
            isValidConfirmPassword = false;
            confirm_password.classList.remove("input__error");
            confirm_password.parentNode.nextElementSibling.classList.add("hidden");
        } else {
            isValidConfirmPassword = false;
            this.classList.add("input__error");
            this.parentNode.nextElementSibling.classList.remove("hidden");
        }
    } else {
        isValidConfirmPassword = false;
        this.classList.add("input__error");
        this.parentNode.nextElementSibling.classList.remove("hidden");
    }

    validate(isValidPassword, isValidConfirmPassword);
});

const close = document.querySelector(".close");

if (close) {
  close.addEventListener("click", function () {
    this.parentNode.classList.add("hidden");
  });
}

password.addEventListener("keypress", function (event) {
  if (event.key === " " || event.keyCode === 32) {
    event.preventDefault();
  }
});

confirm_password.addEventListener("keypress", function (event) {
  if (event.key === " " || event.keyCode === 32) {
    event.preventDefault();
  }
});
