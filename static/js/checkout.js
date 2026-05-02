const checkoutButton = document.querySelector("[data-checkout-button]");
const checkoutStatus = document.querySelector("[data-checkout-status]");

const setCheckoutStatus = (message, isError) => {
    if (!checkoutStatus) {
        return;
    }

    checkoutStatus.textContent = message;
    checkoutStatus.classList.toggle("error", isError);
};

if (checkoutButton) {
    checkoutButton.addEventListener("click", async () => {
        const publicKey = checkoutButton.dataset.publicKey;
        const buyUrl = checkoutButton.dataset.buyUrl;

        if (!publicKey || !buyUrl || typeof Stripe === "undefined") {
            setCheckoutStatus("Stripe checkout is not configured.", true);
            return;
        }

        checkoutButton.disabled = true;
        setCheckoutStatus("Creating Stripe checkout session...", false);

        try {
            const response = await fetch(buyUrl, {
                method: "GET",
                headers: {
                    Accept: "application/json",
                },
                credentials: "same-origin",
            });
            const payload = await response.json();

            if (!response.ok) {
                throw new Error(payload.error || "Checkout session was not created.");
            }

            const stripe = Stripe(publicKey);
            const redirectResult = await stripe.redirectToCheckout({ sessionId: payload.id });

            if (redirectResult.error) {
                throw new Error(redirectResult.error.message);
            }
        } catch (error) {
            setCheckoutStatus(error.message, true);
            checkoutButton.disabled = false;
        }
    });
}
