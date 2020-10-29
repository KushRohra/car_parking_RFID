document.getElementById("price_2").addEventListener("keyup", wheeler2);

function wheeler2() {
    document.getElementById("price2_form").innerHTML = ``;
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
    document.getElementById("price2_form").innerHTML = price2_form;
}