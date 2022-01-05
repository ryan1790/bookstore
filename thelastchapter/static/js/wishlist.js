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
		container.appendChild(close);
		container.appendChild(title);
		container.appendChild(body);
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
			} else {
				wishlistDropdown.setAttribute('data-expanded', 'true');
			}
		}
		document.querySelectorAll('[data-expanded="true"]').forEach(dropdown => {
			if (dropdown === wishlistDropdown) return;
			dropdown.setAttribute('data-expanded', 'false');
		});
	}

	function handleClose(e) {
		if (e.target.matches('.popup-close')) {
			document.querySelector('.popup-container').remove();
		}
	}

	document.addEventListener('click', handleWishExpand);
	document.addEventListener('click', handleWishSend);
	document.addEventListener('click', handleClose);
}
