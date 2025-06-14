const linguaPagina = document.documentElement.lang; // Prende la lingua della pagina
const ultimaLinguaUsata = localStorage.getItem('ultima_lingua_usata');

if (ultimaLinguaUsata && ultimaLinguaUsata !== linguaPagina) {
        // reindirizza
        const url = window.location.pathname;
        const newUrl = url.replace(`/${linguaPagina}/`, `/${ultimaLinguaUsata}/`);
        window.location.replace(newUrl);
}


document.addEventListener('DOMContentLoaded', () => {
    //TODO: inserire controollo su esistenza di laguage switcher ..
    const lang_items = document.getElementById('lang_items').getElementsByTagName('a');
    for (element of lang_items) {

        element.addEventListener('click', function (event) {

            localStorage.setItem('ultima_lingua_usata', event.currentTarget.dataset.ultima_lingua_usata); // Salva la lingua selezionata
        });
    }
});