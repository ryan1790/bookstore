function getScrollElement(target) {
	if (target.matches('[data-left-scroll]')) {
		return target.nextElementSibling;
	}

	if (target.matches('[data-right-scroll]')) {
		return target.previousElementSibling;
	}

	if (target.closest('[data-left-scroll]')) {
		return target.closest('[data-left-scroll]').nextElementSibling;
	}

	if (target.closest('[data-right-scroll]')) {
		return target.closest('[data-right-scroll]').previousElementSibling;
	}
}

document.addEventListener('click', e => {
	const isScrollLeft = e.target.matches('[data-left-scroll]') || e.target.closest('[data-left-scroll]');
	const isScrollRight = e.target.matches('[data-right-scroll]') || e.target.closest('[data-right-scroll]');
	if (isScrollLeft) {
		const scrollElement = getScrollElement(e.target);
		const currentScroll = scrollElement.scrollLeft;
		const options = { top: 0, left: currentScroll - 250, behavior: 'smooth' };
		scrollElement.scrollTo(options);
	} else if (isScrollRight) {
		const scrollElement = getScrollElement(e.target);
		const currentScroll = scrollElement.scrollLeft;
		const options = { top: 0, left: currentScroll + 250, behavior: 'smooth' };
		scrollElement.scrollTo(options);
	}
});
