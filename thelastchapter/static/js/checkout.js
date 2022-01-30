const button = document.querySelector('#submit');
const clientSecret = button.getAttribute('data-secret');
const stripeKey = button.getAttribute('data-key');
const stripe = Stripe(stripeKey);
const appearance = {
	theme: 'night',
	variables: {
		colorPrimary: '#7dadd9',
		colorBackground: '#30313d'
	}
};
const items = [ { id: 'xl-tshirt' } ];

async function handleSubmit(e) {
	e.preventDefault();
	setLoading(true);
	const { error } = await stripe.confirmPayment({
		elements,
		confirmParams: {
			return_url: 'http://127.0.0.1:5000/cart/checkout/status'
		}
	});
	if (error.type === 'card_error' || error.type === 'validation_error') {
		showMessage(error.message);
	} else {
		showMessage(`${error.type} ${error.message}`);
		// showMessage('An unexpected error occured.');
	}
	setLoading(false);
}

function showMessage(messageText) {
	const messageContainer = document.querySelector('#payment-message');
	messageContainer.classList.remove('hidden');
	messageContainer.textContent = messageText;
	setTimeout(function() {
		messageContainer.classList.add('hidden');
		messageText.textContent = '';
	}, 4000);
}

function setLoading(isLoading) {
	if (isLoading) {
		// Disable the button and show a spinner
		document.querySelector('#submit').disabled = true;
		document.querySelector('#spinner').classList.remove('hidden');
		document.querySelector('#button-text').classList.add('hidden');
	} else {
		document.querySelector('#submit').disabled = false;
		document.querySelector('#spinner').classList.add('hidden');
		document.querySelector('#button-text').classList.remove('hidden');
	}
}

const elements = stripe.elements({ clientSecret, appearance });
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');
const form = document.getElementById('payment-form');
form.addEventListener('submit', handleSubmit);
