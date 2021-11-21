var form = document.getElementById("changepw-form");
var email = document.getElementById("changepw-email");
var password = document.getElementById("changepw-password");
var repassword = document.getElementById("changepw-repassword");
var verifier = document.getElementById("changepw-verifier");
var salt = document.getElementById("changepw-salt");

function submitForm() {
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
  form.submit();
}
