document.addEventListener('click', e => {
	const isDropdownButton = e.target.matches('[data-dropdown-button]');
	if (!isDropdownButton && e.target.closest('[data-dropdown]') != null) return;
	let currentDropdown;
	if (isDropdownButton) {
		currentDropdown = e.target.closest('[data-dropdown]');
		currentDropdown.classList.toggle('active');
	}
	document.querySelectorAll('[data-dropdown].active').forEach(dropdown => {
		if (dropdown === currentDropdown) return;
		dropdown.classList.remove('active');
	});
});

function handleOpen(e) {
	console.log('here', e.target);
	const slideMenu = document.querySelector('.slide-menu');
	const slideTop = document.querySelector('.slide-menu-top');
	const closeMenu = document.querySelector('.close-slide-menu');
	slideMenu.setAttribute('data-show-menu', 'true');
	slideTop.setAttribute('data-show-menu', 'true');
	closeMenu.setAttribute('data-show-menu', 'true');
	document.body.setAttribute('data-prevent-scroll', 'true');
}

function handleClose(e) {
	console.log('there', e.target);
	const slideMenu = document.querySelector('.slide-menu');
	const slideTop = document.querySelector('.slide-menu-top');
	const closeMenu = document.querySelector('.close-slide-menu');
	slideMenu.setAttribute('data-show-menu', 'false');
	slideTop.setAttribute('data-show-menu', 'false');
	closeMenu.setAttribute('data-show-menu', 'false');
	document.body.setAttribute('data-prevent-scroll', 'false');
}

function handleSearch(e) {
	if (e.keyCode !== 13) return;
	query = search.value;
	if (query.length === 0) return;
	window.location.href = `/search?query=${query}`;
}

const openSlide = document.querySelector('.open-slide-menu');
const closeSlide = document.querySelector('.close-slide-menu');
const search = document.querySelector('#search');

openSlide.addEventListener('click', handleOpen);
closeSlide.addEventListener('click', handleClose);
search.addEventListener('keyup', handleSearch);
