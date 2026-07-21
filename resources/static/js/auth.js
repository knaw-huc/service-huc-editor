async function login(e, app) {
    console.log(e)
    e.preventDefault()

    const username = document.getElementById("username").value
    const password = document.getElementById("password").value

    const data = new FormData();
    data.append("username", username)
    data.append("password", password)

    const response = await fetch("/app/" + app + "/auth/token", {
        method: "POST",
        headers: {
            'Accept': 'application/json',
        },
        body: data
    })


    const json = await response.json();

    if (response.status === 401) {
        document.getElementById("response").setHTML(json.detail)
        return false;
    }

    console.log(json)

    localStorage.setItem("token_" + app, json.access_token)
    localStorage.setItem("refresh_" + app, json.refresh_token)

    const redirect = localStorage.getItem("redirect_" + app)

    localStorage.removeItem("login_message_" + app)
    if (redirect) {
        localStorage.removeItem("redirect_" + app)
        window.location.replace(redirect)
        return false;
    }

    window.location.replace("/app/" + app)
    return false;
}

async function refreshToken(app) {
    const refresh = localStorage.getItem("refresh_" + app);

    const response = await fetch("/app/" + app + "/auth/refresh", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            refresh_token: refresh
        })
    })

    console.log(response)

    if (response.status !== 200) {
        goToLogin(app, "Your session has expired.")
        return null;
    }
    const json = await response.json()

    localStorage.setItem("token_" + app, json.access_token)
    localStorage.setItem("refresh_" + app, json.refresh_token)

    return json.access_token
}

async function getToken(app) {
    console.log("Get token for " + app)

    let token;

    await navigator.locks.request("token_" + app, async (lock) => {
        token = localStorage.getItem("token_" + app);
        if (!token) {
            return token
        }
        const body = JSON.parse(atob(token.split(".")[1]))
        const expDate = new Date(body.exp * 1000)

        const valid = expDate > Date.now()

        if (!valid) {
            console.log("Token expired.. refreshing")
            token = await refreshToken(app)
        }
    })

    return token
}

function goToLogin(app, message = "You need to log in to view this page.") {
    localStorage.setItem("redirect_" + app, window.location.pathname)
    localStorage.setItem("login_message_" + app, message)

    window.location.replace("/app/" + app + "/login")
}