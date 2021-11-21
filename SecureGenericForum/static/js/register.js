var form = document.getElementById("register-form");
var uname = document.getElementById("register-name");
var email = document.getElementById("register-email");
var password = document.getElementById("register-password");
var repassword = document.getElementById("register-repassword");
var verifier = document.getElementById("register-verifier");
var salt = document.getElementById("register-salt");

function submitForm() {
  var namepattern = /(?:\s*[a-zA-Z0-9]{1,50}\s*)/;
  if (uname.value == null || uname.value == "") {
    alert("Name must be filled out");
    return false;
  } else if (uname.value.length > 50) {
    alert(
      "Name must be at least 1 Characters and not more than 50 Characters"
    );
    return false;
  } else if (!uname.value.match(namepattern)) {
    alert("Please enter a valid Name with only alphanumeric");
    return false;
  }
  var emailpattern = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$/;
  if (email.value == null || email.value == "") {
    alert("Email must be filled out");
    return false;
  } else if (!email.value.match(emailpattern)) {
    alert("Please enter a valid email address");
    return false;
  }
  if (password.value == null || password.value == "") {
    alert("Password must be filled out");
    return false;
  } else if (password.value.length < 12) {
    alert("Password must be at least 12 Characters");
    return false;
  }
  if (repassword.value == null || repassword.value == "") {
    alert("Password Confirmation must be filled in");
    return false;
  } else if (password.value != repassword.value) {
    alert("Password do not match");
    return false;
  }
  var account = generateAccount(email.value, password.value);
  verifier.value = account.verifier;
  salt.value = account.salt;
  password.disabled = true;
  repassword.disabled = true;
  form.submit();
}
