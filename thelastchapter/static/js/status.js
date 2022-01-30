const stripe = Stripe(STRIPE_KEY);
const clientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');

stripe.retrievePaymentIntent(clientSecret).then(({ paymentIntent }) => {
	const message = document.querySelector('#message');
	switch (paymentIntent.status) {
		case 'succeeded':
			message.innerText = 'Success! Payment received.';
			break;

		case 'processing':
			message.innerText = "Payment processing. We'll update you when payment is received.";
			break;

		case 'requires_payment_method':
			message.innerText = 'Payment failed. Please try another payment method';
			// redirect to attempt again
			break;

		default:
			message.innerText = 'Something went wrong.';
			break;
	}
});