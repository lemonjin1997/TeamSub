var form = document.getElementById("login-form");
var email = document.getElementById("login-email");
var password = document.getElementById("login-password");
var clientpub = document.getElementById("login-clientpub");
var m1 = document.getElementById("login-m1");

function submitForm() {
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
  password.disabled = true;
  verifyAccount(email.value, password.value, csrf_token)
    .then(function (response) {
      clientpub.value = response.userpubkey_A;
      m1.value = response.M1;
      sessionStorage.setItem("Encryption Key", response.S);
      form.submit();
    })
    .catch(function (error) {
      clientpub.value = 0;
      m1.value = 0;
      form.submit();
    });
}
