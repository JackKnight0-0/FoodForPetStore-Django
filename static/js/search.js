let searchInput = document.getElementById('searchInput');
let searchResults = document.getElementById('searchResults')
searchInput.addEventListener("input", function (event) {
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const results = JSON.parse(xhr.responseText);
            if (results.data.length > 0) {
                getSuggestions(results.data);
            }
        } else {
            searchResults.innerHTML = '';
        }
    };
    if (event.target.value) {
        console.log()
        xhr.open('GET', `api/suggestions/?q=` + event.target.value, true);
        xhr.send();
    } else {
        searchResults.innerHTML = '';
    }
})

function getSuggestions(suggestions) {

    searchResults.innerHTML = '';
    if (suggestions.length > 0) {
        searchResults.classList.add('active');
        suggestions.forEach(suggestion => {
            const suggestionElement = document.createElement('div');
            suggestionElement.textContent = suggestion;
            suggestionElement.onclick = () => {
                searchInput.value = suggestion;
                searchResults.classList.remove('active');
                document.getElementById('searchForm').submit()
            };
            searchResults.appendChild(suggestionElement);
        });
    } else {
        searchResults.classList.remove('active');
    }
}

document.addEventListener('click', (event) => {
    if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
        searchResults.classList.remove('active');
    }
});