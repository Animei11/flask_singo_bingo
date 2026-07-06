lobbyCode = document.getElementById('lobby-code').value;
someoneHasBingo = false;

// Starting point for startGame
loadClassicModePlaylists();

// Displays 4 playlists for the user to choose from (TODO: Will be a wheel later)
async function loadClassicModePlaylists() {
    try {
        const res = await fetch('/spotify/getplaylists?mode=classic');
        const playlists = await res.json();
        const container = document.getElementById('playlist-selection-container');

        playlists.forEach(playlist => {
            const playlistCell = document.createElement('div');
            playlistCell.textContent = playlist.playlist_name;
            playlistCell.addEventListener('click', async () => {
                const res = await fetch("/spotify/playlists/selectedPlaylist", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        playlist_id: playlist.id,
                        playlist_uri: playlist.playlist_uri,
                        playlist_name: playlist.playlist_name,
                        lobby_code: lobbyCode
                    })
                });
                const data = await res.json();
                if (data.auth_required) {
                    window.location.href = "/spotify/login";
                    return;
                }
                else if (data.ok) {
                    hideDiv('playlist-selection-container');
                    showDiv('playlist-visual-container');
                    const playlistVisualContainer = document.getElementById('playlist-visual-container');
                    const playlistTitle = document.createElement('h2');
                    playlistTitle.textContent = `Playlist Chosen: ${playlist.playlist_name}`;
                    playlistVisualContainer.appendChild(playlistTitle);
                    displaySongCurrentlyPlaying();
                }
            });
            container.appendChild(playlistCell);
        });
    } catch (err) {
        console.error(err);
    }
}

// Delay timer 
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Shows which song is playing (mostly used to debug)
// TODO: Add a reolad for when host choses playlist or not even run it till then
async function displaySongCurrentlyPlaying() {
    try {
        // Step 1: Retrieve playlist
        const response = await fetch(`/spotify/playlists/getMasterPlaylist?lobby_code=${lobbyCode}`);
        const data = await response.json();
        const songDetails = data.songs;
        showDiv('song-visual-container');
        const songVisualContainer = document.getElementById('song-visual-container');

        // Plays songs until someone gets bingo
        for (const song of songDetails) {
            const songTitle = song.song_name;
            const songUri = song.song_uri;
            // Step 2: Tell backend to play song
            await fetch(`/spotify/playlists/playsong?song_uri=${encodeURIComponent(songUri)}`);
            // Step 3: Display currently playing song (debugging purposes)
            songVisualContainer.innerHTML = ""; // clear previous song
            const songEl = document.createElement('p');
            songEl.textContent = `Song Currently Playing: ${songTitle}`;
            songVisualContainer.appendChild(songEl);
            // Step 4: Play 20 seconds and silence for 5 
            await delay(5000); // Play song for 15
            await fetch('/spotify/playlists/stopsong');
            await delay(5000); // Stop song for 5
            await fetch(`/spotify/playlists/nextIndex?lobby_code=${lobbyCode}`); // Move to next song in playlist
            // Step 5: Check for bingo
            if (someoneHasBingo) {
                console.log(`/gameOver/${lobbyCode}`)
                window.location.href = `/gameOver/${lobbyCode}`;
                return;
            }
        }
    } catch (error) {
        console.error('Error fetching songs:', error);
    }
}