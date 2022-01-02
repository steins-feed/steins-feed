function toggle_checkbox(fieldset_id) {
    const stat = document.getElementById(fieldset_id);
    const inputs = stat.getElementsByTagName("input");

    if (inputs[0].checked) {
        for (let input_it of inputs) {
            input_it.checked = true;
        }
    } else {
        for (let input_it of inputs) {
            input_it.checked = false;
        }
    }
}

function prove_checkbox(fieldset_id) {
    const stat = document.getElementById(fieldset_id);
    const inputs = stat.getElementsByTagName("input");

    for (let input_ct = 1; input_ct < inputs.length; input_ct++) {
        if (!inputs[input_ct].checked) {
            inputs[0].checked = false;
            return;
        }
    }

    inputs[0].checked = true;
}
