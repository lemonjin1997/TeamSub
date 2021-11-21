var form = document.getElementById("forget-form");
var email = document.getElementById("forget-email");

function submitForm() {
  var emailpattern = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$/;
  if (email.value == null || email.value == "") {
    alert("Email must be filled out");
    return false;
  } else if (!email.value.match(emailpattern)) {
    alert("Please enter a valid email address");
    return false;
  }
  form.submit();
}
