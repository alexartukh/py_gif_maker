function get_auth_token(login, password) {
    jQuery('#gif_maker_login').text(login);
    jQuery('#gif_maker_password').text(password);

    jQuery.ajax({
        url: "/login",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            login: login,
            password: password
        }),
        success: function (response) {
            if (response.error) {
                console.error("GIF MAKER - Login failed:", response.message);
                return;
            }
            var token = response.token;
            console.log("GIF MAKER - Got token:", token);

            // сохраняем как глобальную переменную, чтобы использовать дальше на странице
            window.gifMakerAuthToken = token;
            sessionStorage.setItem("authToken", token);
        },
        error: function (xhr) {
            console.error("GIF MAKER - Request failed:", xhr.status, xhr.responseText);
        }
    });
}
