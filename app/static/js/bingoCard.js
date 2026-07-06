loadAvatar();
loadBingoCard();

async function verifyClickedTile(event) {
    const clickedTile = event.target;
    const lobbyCode = document.getElementById('lobby-code').value;
    const username = encodeURIComponent(document.getElementById('username').value);
    console.log("Clicked tile ID: ", clickedTile.id);
    if (clickedTile.id === 'free-space') {
        // TODO: Add a fetch to update back end that this tile has been marked for this player
        clickedTile.classList.add('marked');
        return;
    }
    try {
        const response = await fetch(`/spotify/playlists/verifySong?lobby_code=${lobbyCode}&song_title=${clickedTile.id}&username=${username}`);
        res = await response.json();
        console.log("Response from server: ", res);
        if (res.ok) { clickedTile.classList.add('marked') };
        if (res.hasBingo) {
            alert("BINGO! You win!");
        }
    } catch (error) {
        console.error('Error verifying clicked tile:', error);
    }
}

// Fetch Playlist JSON and build bingo card
async function loadBingoCard() {
    try {
        const lobbyCode = document.getElementById('lobby-code').value;
        const username = document.getElementById('username').value;
        const response = await fetch(`/spotify/playlists/getPlayersSongs?lobby_code=${lobbyCode}&username=${encodeURIComponent(username)}`);
        const data = await response.json();

        // Create header
        const headerRow = document.getElementById('bingo-header-row');
        const title = ['B', 'I', 'N', 'G', 'O'];

        title.forEach(letter => {
            const headerCell = document.createElement('div');
            headerCell.className = 'bingo-letter';
            headerCell.textContent = letter;
            headerRow.appendChild(headerCell);
        });

        // Add songs to bingo grid
        const card = document.getElementById('bingo-grid');
        console.log("Marked tiles from server: ", data.marked_tiles);
        for (let i = 0; i < 25; i++) {
            const row = Math.floor(i / 5);
            const col = i % 5;
            const tile = document.createElement('div');
            tile.className = 'song-tile';
            tile.dataset.row = row;
            tile.dataset.col = col;
            tile.id = data.songs[i];
            tile.textContent = data.songs[i];
            const isMarked = data.marked_tiles.some(
                ([r, c]) => r === row && c === col
            );
            if (isMarked) {
                tile.classList.add('marked');
            }
            tile.addEventListener('click', verifyClickedTile);
            card.appendChild(tile);
        }
    } catch (error) {
        console.error('Error fetching JSON:', error);
    }
}

async function loadAvatar() {
    const username = document.getElementById("username").value;
    if (!username) {
        console.error("Username not found");
        return;
    }
    console.log("Loading avatar for username:", username);
    try {
        const response = await fetch(`/db/getPlayerAvatar?username=${encodeURIComponent(username)}`);
        const data = await response.json();
        console.log("Avatar response data:", data);
        if (data.ok && data.avatar_file_name) {
            const avatarDisplay = document.getElementById('avatar-display');
            avatarDisplay.className = 'avatar-display';
            avatarDisplay.innerHTML = `<img src="/static/imgs/avatars/${data.avatar_file_name}" alt="Player Avatar" class="avatar-image">`;
        } else {
            console.error("Failed to load player avatar:", data.error);
        }
    } catch (error) {
        console.error("Error loading player avatar:", error);
    }
}