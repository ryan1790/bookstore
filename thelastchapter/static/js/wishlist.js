if (document.querySelector('[data-wishlist-button]') != null) {
	function timedPopup(status, message) {
		const prev = document.querySelector('.popup-container');
		if (prev) prev.remove();
		const container = document.createElement('div');
		container.classList.add('popup-container', `popup-${status}`);
		const close = document.createElement('div');
		close.classList.add('popup-close');
		close.textContent = 'X';
		const title = document.createElement('h2');
		title.classList.add('popup-title');
		title.textContent = status === 'success' ? 'Success' : 'Error';
		const body = document.createElement('p');
		body.classList.add('popup-body');
		body.textContent = message;
		const animate = document.createElement('div');
		animate.classList.add('remove-timer-animation');
		container.appendChild(close);
		container.appendChild(title);
		container.appendChild(body);
		container.appendChild(animate);
		document.querySelector('body').appendChild(container);
		setTimeout(() => container.remove(), 3000);
	}

	async function handleWishSend(e) {
		if (e.target.matches('span.list-name')) {
			const options = {
				credentials: 'same-origin',
				method: 'POST'
			};
			const book_id = e.target.previousElementSibling.value;
			const list_id = e.target.nextElementSibling.value;
			const url = `/lists/${list_id}/${book_id}/add`;
			const res = await handleRequest(url, options);
			if (res) {
				const { dbStatus, message } = res;
				timedPopup(dbStatus, message);
			}
			e.target.closest('[data-expanded]').setAttribute('data-expanded', 'false');
		}
	}

	async function handleRequest(url, options) {
		const res = await fetch(url, options);
		if (!res.ok) {
			timedPopup('error', res.status);
			return null;
		} else {
			return await res.json();
		}
	}

	function handleWishExpand(e) {
		const isWishlistButton =
			e.target.matches('[data-wishlist-button]') || e.target.closest('[data-wishlist-button]');
		if (!isWishlistButton && e.target.closest('[data-wishlist-dropdown]') != null) return;
		let wishlistDropdown;
		if (isWishlistButton) {
			wishlistDropdown = e.target.closest('[data-expanded]');
			const b = wishlistDropdown.getAttribute('data-expanded');
			if (b === 'true') {
				wishlistDropdown.setAttribute('data-expanded', 'false');
				handleResetNewListForm();
			} else {
				wishlistDropdown.setAttribute('data-expanded', 'true');
			}
		}
		document.querySelectorAll('[data-expanded="true"]').forEach(dropdown => {
			if (dropdown === wishlistDropdown) return;
			dropdown.setAttribute('data-expanded', 'false');
		});

		document.querySelectorAll('[data-expand-new-list="true"]').forEach(newForm => {
			if (newForm.closest('[data-wishlist-dropdown]') === wishlistDropdown?.closest('[data-wishlist-dropdown'))
				return;
			newForm.setAttribute('data-expand-new-list', 'false');
		});
	}

	function handleClose(e) {
		if (e.target.matches('.popup-close')) {
			document.querySelector('.popup-container').remove();
		}
	}

	function handleNewListForm(e) {
		e.target.setAttribute('data-expand-new-list', 'true');
	}

	function handleResetNewListForm() {
		document.querySelectorAll('[data-expand-new-list="true"]').forEach(node=>{
			node.setAttribute('data-expand-new-list', 'false');
		});
		document.querySelectorAll('.list-search').forEach(input=>{
			input.textContent = '';
		});
	}

	async function handleCreateNewList(e) {
		e.preventDefault();
		const formData = new FormData(this);
		const options = {
			method: 'POST',
			body: formData,
			credentials: 'same-origin'
		};
		const url = '/lists/create';
		const res = await handleFetchNewList(url, options);
		if (res) {
			console.log(res)
			const { dbStatus, message, list_id: listId, list_name: listName } = res;
			timedPopup(dbStatus, message);
			addNewListToDisplay(listId, listName);
			handleResetNewListForm();
		}
		e.target.closest('[data-expanded]').setAttribute('data-expanded', 'false');
	}

	async function handleFetchNewList(url, options) {
		const res = await fetch(url, options);
		if (!res.ok) {
			timedPopup('error', res.status);
			return null;
		} else {
			return await res.json();
		}
	}

	function handleSearch(e) {
		const filter = e.target.value.toLowerCase();
		console.log(filter);
		let next = e.target.nextElementSibling
		while (next?.matches('.list-name-container')) {
			if (!next.textContent.toLowerCase().includes(filter)) {
				next.setAttribute('data-hidden', 'true');
			} else {
				next.setAttribute('data-hidden', 'false');
			}
			next = next.nextElementSibling;
		}
	}

	function addNewListToDisplay(listId, listName) {
		document.querySelectorAll('.wishlist-form').forEach(el => {

			const bookId = el.querySelector('[name="book-id"]').value;
			const lastEl = el.querySelector('.new-list');

			const container = document.createElement('div');
			container.classList.add('list-name-container');
			container.setAttribute('data-hidden', 'false');

			const bookInput = document.createElement('input');
			bookInput.setAttribute('type', 'hidden');
			bookInput.setAttribute('name', 'book-id');
			bookInput.setAttribute('value', bookId);

			const name = document.createElement('span');
			name.classList.add('list-name');
			name.textContent = listName;

			const listInput = document.createElement('input');
			listInput.setAttribute('type', 'hidden');
			listInput.setAttribute('name', 'list-id');
			listInput.setAttribute('value', listId);

			container.appendChild(bookInput);
			container.appendChild(name);
			container.appendChild(listInput);

			el.insertBefore(container, lastEl);
		});
	}

	document.querySelectorAll('[data-expand-new-list]').forEach(form => {
		form.addEventListener('click', handleNewListForm);
	});

	document.querySelectorAll('.create-list-form').forEach(form => {
		console.log(form);
		form.addEventListener('submit', handleCreateNewList);
	});

	document.querySelectorAll('.list-search').forEach(search => {
		search.addEventListener('input', handleSearch);
	});

	document.addEventListener('click', handleWishExpand);
	document.addEventListener('click', handleWishSend);
	document.addEventListener('click', handleClose);
}
