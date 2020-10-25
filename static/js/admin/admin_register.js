var errorArea = document.getElementById('formValidator');

document.getElementById("repeat_password").addEventListener("keyup", checkPassword);
document.getElementById("enter_2_wheeler").addEventListener("click", wheeler2);
document.getElementById("enter_4_wheeler").addEventListener("click", wheeler4);

function checkPassword() {
    var repeat_password = document.getElementById("repeat_password").value;
    var password = document.getElementById('password').value;
    if(password!=repeat_password) {
        errorArea.innerHTML = 'Passwords do not match';
        errorArea.style.color = 'red';
    }
    else {
        errorArea.innerHTML = 'Both passwords match';
        errorArea.style.color = 'green';
    }
}

function wheeler2() { 
    document.getElementById("form_2").innerHTML = ``;
    var price2_slots = document.getElementById("price_2").value;
    var price2_form = `<form class="col s12">`;
    for(var i=0;i<price2_slots;i++) {
        price2_form += `Enter: <input id="form2_`+(i+1)+`" type="text"></input>`;
    }
    document.getElementById("form_2").innerHTML = price2_form;
    price2_form = `</form>`;
}

function wheeler4() { 
    document.getElementById("form_4").innerHTML = ``;
    var price4_slots = document.getElementById("price_4").value;
    var price4_form = `<form class="s12">`;
    for(var i=0;i<price4_slots;i++) {
        price4_form += `Enter: <input id="form4_`+(i+1)+`" type="text"></input>`;
    }
    document.getElementById("form_4").innerHTML = price4_form;
    price4_form = `</form>`;
}