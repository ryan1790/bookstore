function setup() {
	const totalDisplay = document.querySelector('#total');
	const quantities = document.querySelectorAll('.number-input');
	const prices = document.querySelectorAll('.price-value');
	const totals = document.querySelectorAll('.price-total');
	const hInputs = document.querySelectorAll('.book-quantities-input');
	const compare = [ 0, 1, 2, 3, 4, 5 ];

	function updateTotal() {
		let total = 0;
		totals.forEach(subtotal => (total += parseFloat(subtotal.textContent)));
		const formatted = Math.round(total * 100) / 100;
		totalDisplay.textContent = formatted.toFixed(2);
	}

	for (let i = 0; i < prices.length; i++) {
		function handleInputChange(e) {
			const el = e.target;
			if (!compare.includes(parseInt(el.value))) el.value = 1;
			hInputs[i].value = el.value;
			const value = parseInt(el.value);
			newTotal = value * parseFloat(prices[i].textContent);
			totals[i].textContent = (Math.round(newTotal * 100) / 100).toFixed(2);
			updateTotal();
		}
		quantities[i].addEventListener('change', handleInputChange);
	}
}

if (document.querySelector('#total')) setup();
