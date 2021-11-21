var form = document.getElementById("otp-form");
var otp = document.getElementById("otp");

function submitForm() {
  var cipherdict = encrypt(otp.value);
  otp.value = JSON.stringify(cipherdict);
  form.submit();
}
