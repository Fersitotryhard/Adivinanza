document.getElementById("btn-register").addEventListener("click", register);
function register(){
    const name = document.getElementById("name").value;
    const email = document.getElementById("account").value;
    const password = document.getElementById("password").value;

    if(name === "") {
        Swal.fire({
            title: 'Nombre no ingresado',
            text: 'Debe ingresar su nombre.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }

    if(email === "") {
        Swal.fire({
            title: 'Correo electrónico no ingresado',
            text: 'Debe ingresar su correo electrónico.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }

    if(password === "") {
        Swal.fire({
            title: 'Contraseña no ingresada',
            text: 'Debe ingresar una contraseña.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }

    const data = {
        name: name,
        email: email,
        password: password
    }

    fetch('api/users', {
        method:"POST",
        headers: { "Content-Type": "application/json"},
        body: JSON.stringify(data)
    }). then(response => response.json())
    .then(result =>  {
        Swal.fire({
            title: result.success ? 'Cuenta creada' : 'Error al crear la cuenta',
            text: result.message,
            icon: result.success ? 'success' : 'error',
            confirmButtonText: 'Aceptar'
        }).then(() => {
            if(result.success){
                window.location.href = "/";
            }
        });
    })
    .catch(error => {
        console.error(error);
    })
    


}