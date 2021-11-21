function submitForm(id) {
  var form = document.getElementById(id);
  var textarea_list = form.querySelectorAll("textarea"); // returns NodeList
  var textarea_array = [...textarea_list]; // converts NodeList to Array
  textarea_array.forEach((textarea) => {
    var temp = textarea.value;
    textarea.style = "display:none;";
    textarea.value = JSON.stringify(encrypt(temp));
  });
  form.submit();
}
