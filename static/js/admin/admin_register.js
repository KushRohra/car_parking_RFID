var errorArea = document.getElementById('formValidator');
var submitBtn = document.getElementById('submitBtn');

document.getElementById("password").addEventListener("keyup", checkPassword);
document.getElementById("repeat_password").addEventListener("keyup", checkPassword);
document.getElementById("price_2").addEventListener("keyup", wheeler2);
document.getElementById("price_4").addEventListener("keyup", wheeler4);

function checkPassword() {
    var repeat_password = document.getElementById("repeat_password").value;
    var password = document.getElementById('password').value;
    if(password!=repeat_password) {
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

function wheeler2() { 
    document.getElementById("form_2").innerHTML = ``;
    var price2_slots = document.getElementById("price_2").value;
    var price2_form = ``;
    for(var i=0;i<price2_slots;i++) {
        price2_form += `<div class="row">
                            <div class="col s4">
                                Enter time: <input name="form_2_1_`+(i+1)+`" type="number" placeholder="Enter time in hrs" min="0" required></input>
                            </div>
                            <div class="col s4">
                                Enter price: <input name="form_2_2_`+(i+1)+`" type="number" placeholder="Enter cost in Rs." min="0" required></input>
                            </div>
                        </div>`;
    }
    document.getElementById("form_2").innerHTML = price2_form;
}

function wheeler4() { 
    document.getElementById("form_4").innerHTML = ``;
    var price4_slots = document.getElementById("price_4").value;
    var price4_form = ``;
    for(var i=0;i<price4_slots;i++) {
        price4_form += `<div class="row">
                            <div class="col s4">
                                Enter time: <input name="form_4_1_`+(i+1)+`" type="number" placeholder="Enter time in hrs" min="0" required></input>
                            </div>
                            <div class="col s4">
                                Enter price: <input name="form_4_2_`+(i+1)+`" type="number" placeholder="Enter cost in Rs." min="0" required></input>
                            </div>
                        </div>`;
    }
    document.getElementById("form_4").innerHTML = price4_form;
}