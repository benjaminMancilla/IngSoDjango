// Verdad, que el usuario no debiese poder registrarse,
// Se implementará validaciones del registro (por si acaso), y también otras funciones (quizá no necesarias)

//Registro && Ingreso(Opcional)
const validate_password = (password) => {
    const re = /[A-Z]/;
    let passwordLength = password.length >=6;
    let upperValidation = re.test(password);
    if (passwordLength && upperValidation) {
        return true;
    };
    return false;
};

const validate_user = (userName) => {
    return (userName.length >= 3);
};


const validate_login = () => {
    loginData = document.forms["loginForm"];
    user = loginData["userName"];
    password = loginData["userPassword"];

    let invalidInputs = [];
    let isValid = true;
    const setInvalidInput = (inputName) => {
        invalidInputs.push(inputName);
        isValid &&= false;
    }

    let notificationBox = document.getElementById("notificationBox");
    let notificationList = document.getElementById("notificationList");

    if ((!validate_user(user)) || (!validate_password(password))) {
        setInvalidInput("error");
    };
    if (!isValid){
        notificationList.textContent = "";
        for (let input of invalidInputs) {
            let listElement = document.createElement("li");
            listElement.innerText = input;
            notificationList.append(listElement);
        };
        notificationBox.hidden = false;
    }
    // ↑ Decoración.
} 





const button = document.getElementById("sendInfo");
button.addEventListener("click", validate_login);
//Login


