const validateReason = (reason) => {
    if (!reason) return true;
    else {
        // validación de longitud
        let lengthValid = reason.trim().length <= 300;
        return lengthValid;
    }
}

const validateRadio = (radioName) => {
    const radios = document.getElementsByName(radioName);
    for (let radio of radios){
        if (radio.checked){
            return true;
        }
    }
    return false;
}

const validateForm = () => {
    let theForm = document.forms["mainForm"];
    let classCalReason = theForm["calificationReason"];
    let feedback = theForm["necessityFeedback"];
    let 
}