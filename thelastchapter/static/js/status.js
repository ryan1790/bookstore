if (document.querySelector('#message')) {
	const message = document.querySelector('#message');
	const stripe = Stripe(message.getAttribute('data-stripe-key'));
	const clientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');
	console.log(clientSecret);
	stripe.retrievePaymentIntent(clientSecret).then(({ paymentIntent }) => {
		console.log(paymentIntent.status);
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
}
