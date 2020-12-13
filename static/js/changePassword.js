var errorArea = document.getElementById('formValidator');
var submitBtn = document.getElementById('submitBtn');

document.getElementById("password").addEventListener("keyup", checkPassword);
document.getElementById("repeat_password").addEventListener("keyup", checkPassword);

function checkPassword() {
    var repeat_password = document.getElementById("repeat_password").value;
    var password = document.getElementById('password').value;
    if(password=="" && repeat_password=="") {
          errorArea.innerHTML = ' ';
          submitBtn.disabled = false;
    }
    else if(password!=repeat_password) {
        errorArea.innerHTML = 'Passwords do not match';
        errorArea.style.color = 'red';
        submitBtn.disabled = true;
    }
    else {
        errorArea.innerHTML = 'Both passwords match';
        errorArea.style.color = 'green';
        submitBtn.disabled = false;
    }
}
