document.getElementById("btn-login").addEventListener("click", login);

function login() {
    const email = document.getElementById("account").value;
    const password = document.getElementById("password").value;

    if (email === "") {
        Swal.fire({
            title: 'Correo no ingresado',
            text: 'Debes ingresar tu correo electrónico.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }

    if (password === "") {
        Swal.fire({
            title: 'Contraseña no ingresada',
            text: 'Debes ingresar tu contraseña.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }

    const data = {
        email: email,
        password: password
    };

    fetch('/api/login', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            Swal.fire({
                title: '¡Bienvenido!',
                text: result.message,
                icon: 'success',
                confirmButtonText: 'Continuar'
            }).then(() => {
                window.location.href = "/home";
            });
        } else {
            Swal.fire({
                title: 'Error al iniciar sesión',
                text: result.message,
                icon: 'error',
                confirmButtonText: 'Aceptar'
            });
        }
    })
    .catch(error => {
        console.error(error);
        Swal.fire({
            title: 'Error',
            text: 'Ocurrió un error inesperado. Intenta de nuevo.',
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
    });
}