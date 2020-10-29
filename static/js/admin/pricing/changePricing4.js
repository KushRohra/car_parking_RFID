document.getElementById("price_4").addEventListener("keyup", wheeler4);

function wheeler4() {
    document.getElementById("price4_form").innerHTML = ``;
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
    document.getElementById("price4_form").innerHTML = price4_form;
}