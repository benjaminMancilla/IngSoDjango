const validateReason = (reason) => {
    if (!reason) return true;
    else {
        // validación de longitud
        let lengthValid = (reason.trim().length <= 300) && (reason.trim().length >= 3);
        return lengthValid;
    };
};

const validateRadio = (radioName) => {
    const radios = document.getElementsByName(radioName);
    for (let radio of radios){
        // if (radio.checked){
        //     return true;
        if (radio.checked) return true;
    };
    return false;
};
const validateCalificationComment = (comment) => {
    if (reasonBlock.hidden) return true;
    if (comment.trim().length <=3) return false;
    // if (!(comment.length >=3)) {
    //     return false;
    // }
    return true;
}

const reasonBlock = document.getElementById("professorCalificationReason");

function hideReasonInput() {
    reasonBlock.hidden = true;
    return;
};

function unhideReasonInput() {
    reasonBlock.hidden = false;
    return;
};

const validateForm = () => {
    let theForm = document.forms["mainForm"];
    let classCalReason = theForm["calificationReason"].value;
    let feedback = theForm["necessityFeedback"].value;
    // let classCal = theForm["classCalification"].value;
    // let professorCal = theForm["professorCalification"].value;
    let hiddenInput = document.getElementById("professorCalReason");
    
    // let 
    
    let invalidInputs = [];
    let isValid = true;
    const setInvalidInput = (inputName) => {
        invalidInputs.push(inputName);
        isValid &&= false;
    };

    if (!validateCalificationComment(hiddenInput.value)){
        setInvalidInput("hiddenInputArea");
        // if(!(hiddenInput.value.trim().length >= 3)){
        //     setInvalidInput("hiddenInputArea")
        // }
        // if (!validateReason(hiddenInput.value)) {
        //     setInvalidInput("hiddenInputArea");
        // };
    };

    if (!validateReason(classCalReason)) {
        setInvalidInput("textArea");
    };
    if (!validateReason(feedback)) {
        setInvalidInput("textArea2");
    };
    if (!validateRadio("classCalification")) {
        setInvalidInput("classCalification");
    };
    if (!validateRadio("professorCalification")) {
        setInvalidInput("professorCalification");
    };


    let notificationBox = document.getElementById("notificationBox");
    let notificationMessage = document.getElementById("notificationMsg");
    let notificationList = document.getElementById("notificationList");
    
    if (!isValid) {
        notificationList.textContent = "";
        for (let input of invalidInputs) {
            let listElement = document.createElement("li");
            listElement.innerText = input;
            notificationList.append(listElement);
        };
        notificationMessage.innerText="Los siguientes campos son inválidos:";
        notificationBox.style.backgroundColor = "#ffdddd";
        notificationBox.style.borderLeftColor = "#f44336";
        notificationBox.hidden = false;
    } else {
        theForm.style.display = "none";
        notificationMessage.innerText = "¿Confirma que desea enviar esta retroalimentación?";
        notificationList.textContent = "";

        notificationBox.style.backgroundColor = "#ddffdd";
        notificationBox.style.borderLeftColor = "#4CAF50";
    
        let submitButton = document.createElement("button");
        submitButton.innerText = "Sí, confirmo";
        submitButton.style.marginRight = "10px";
    
        let backButton = document.createElement("button");
        backButton.innerText = "No, quiero volver al formulario";
        backButton.addEventListener("click", () => {
            theForm.style.display = "block";
            notificationBox.hidden = true;
        });
        submitButton.addEventListener("click", () => {
            notificationMessage.innerText = "Hemos recibido su retroalimentación. Muchas gracias."
            submitButton.hidden = true;
            backButton.hidden = true;
            //theForm.submit();
        })
        notificationList.appendChild(submitButton);
        notificationList.appendChild(backButton);
        notificationBox.hidden = false;
    };
};



let submitBtn = document.getElementById("sendQuestionnaireButton");
submitBtn.addEventListener("click", validateForm);