if (document.querySelector('.cart')) {
	async function handleClick(e) {
		const element = e.target.closest('[data-book-id]');
		const bookId = element.getAttribute('data-book-id');
		const url = `/cart/${bookId}/add`;
		const options = {
			credentials: 'same-origin',
			method: 'POST'
		};
		const res = await handleRequest(url, options);
		if (res) {
			const { dbStatus, message } = res;
			timedPopup(dbStatus, message);
			if (dbStatus === 'success') {
				element.nextElementSibling.removeAttribute('hidden');
				element.remove();
			}
		}
	}

	function createCartLink(e) {
		e.nextElementSibling;
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

	document.querySelectorAll('[data-book-id]').forEach(button => {
		button.addEventListener('click', handleClick);
	});
}
