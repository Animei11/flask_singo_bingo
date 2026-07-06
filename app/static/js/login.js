// Verify lobby code 
document.getElementById("login-form").addEventListener("submit", async function (e) {
    e.preventDefault(); // stop default submission
    const submitLogin = document.getElementById("submit-login");
    const lobbyCodeInput = document.getElementById('lobby-code-input').value.trim().toUpperCase();
    const username = document.getElementById('username').value;
    try {
        // Wait for lobby codes from the server
        const listOfLobbyCodes = await fetchLobbyCode();

        if (listOfLobbyCodes.includes(lobbyCodeInput)) {
            console.log("I'm feeling wheee!")
            addUser(username, lobbyCodeInput);
            submitLogin.disabled = true;
            showAvatarSelection();
        } else {
            console.log("I'm feeling whoooo...")
        }
    } catch (err) {
        console.error("Error fetching lobby codes:", err);
    }
});


async function fetchLobbyCode() {
    const response = await fetch('/db/getLobbyCode');
    const lobbies = await response.json();
    return lobbies;
}


function addUser(username, lobbyCode) {
    fetch("/db/createUser", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
            username: username,
            lobby_code: lobbyCode
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                console.log("User added!");
            } else {
                console.error("Error:", data.error);
            }
        });
}


function addAvatarToUser(avatarId) {
    const username = document.getElementById("username").value;
    fetch("/db/addAvatarSelected", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            username: username,
            avatar_id: avatarId
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                console.log("Avatar saved!");
            } else {
                console.error("Error:", data.error);
            }
        });
}


function showAvatarSelection() {
    const lobbyCodeInput = document.getElementById('lobby-code-input').value.trim().toUpperCase();
    const avatarDiv = document.getElementById('avatar-selection-container');
    hideDiv('login-form-container');
    showDiv('avatar-selection-container');
    // Fetches avatar images from server
    fetch('/db/GetAvatarImages')
        .then(response => response.json())
        .then(avatars => {
            avatars.forEach(avatar => {
                const imgElement = document.createElement('img');
                imgElement.src = avatar.filePath;
                imgElement.id = avatar.id;
                imgElement.className = 'avatar-image';
                imgElement.addEventListener('click', () => {
                    const username = document.getElementById("username").value;
                    fetch("/db/addAvatarSelected", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            username: username,
                            avatar_id: avatar.id
                        })
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.ok) {
                                console.log("Avatar saved!");
                                console.log(`/bingoCard/${lobbyCodeInput}`);
                                window.location.href = `/bingoCard/${lobbyCodeInput}`;
                            } else {
                                console.error("Error:", data.error);
                            }
                        });
                });
                avatarDiv.appendChild(imgElement);
            });
        })
        .catch(error => {
            console.error('Error fetching JSON:', error);
        });
}