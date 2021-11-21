try {
  var h1_list = document.querySelectorAll("h1"); // returns NodeList
  var h1_array = [...h1_list]; // converts NodeList to Array
  h1_array.forEach((h1) => {
    try {
      var temp = JSON.parse(h1.innerHTML);
      h1.innerHTML = decrypt(temp.ciphertext, temp.nonce, temp.tag);
    } catch (err) {}
  });
} catch (err) {}

try {
  var h5_list = document.querySelectorAll("h5"); // returns NodeList
  var h5_array = [...h5_list]; // converts NodeList to Array
  h5_array.forEach((h5) => {
    try {
      var temp = JSON.parse(h5.innerHTML);
      h5.innerHTML = decrypt(temp.ciphertext, temp.nonce, temp.tag);
    } catch (err) {}
  });
} catch (err) {}

try {
  var p_list = document.querySelectorAll("p"); // returns NodeList
  var p_array = [...p_list]; // converts NodeList to Array
  p_array.forEach((p) => {
    try {
      var temp = JSON.parse(p.innerHTML);
      p.innerHTML = decrypt(temp.ciphertext, temp.nonce, temp.tag);
    } catch (err) {}
  });
} catch (err) {}

try {
  var textarea_list = document.querySelectorAll("textarea"); // returns NodeList
  var textarea_array = [...textarea_list]; // converts NodeList to Array
  textarea_array.forEach((textarea) => {
    try {
      var temp = JSON.parse(textarea.value);
      textarea.value = decrypt(temp.ciphertext, temp.nonce, temp.tag);
    } catch (err) {}
  });
} catch (err) {}
