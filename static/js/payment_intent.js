const paymentForm = document.querySelector("[data-payment-intent-form]");
const paymentStatus = document.querySelector("[data-payment-status]");

const setPaymentStatus = (message, isError) => {
    if (!paymentStatus) {
        return;
    }

    paymentStatus.textContent = message;
    paymentStatus.classList.toggle("error", isError);
};

if (paymentForm) {
    const publicKey = paymentForm.dataset.publicKey;
    const intentUrl = paymentForm.dataset.intentUrl;
    const csrfTokenInput = paymentForm.querySelector("[name=csrfmiddlewaretoken]");
    const submitButton = paymentForm.querySelector("button[type=submit]");

    if (publicKey && intentUrl && typeof Stripe !== "undefined") {
        const stripe = Stripe(publicKey);
        const elements = stripe.elements();
        const cardElement = elements.create("card", { hidePostalCode: true });
        cardElement.mount("#card-element");

        paymentForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            submitButton.disabled = true;
            setPaymentStatus("Creating Payment Intent...", false);

            try {
                const response = await fetch(intentUrl, {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfTokenInput ? csrfTokenInput.value : "",
                    },
                    credentials: "same-origin",
                    body: "{}",
                });
                const payload = await response.json();

                if (!response.ok) {
                    throw new Error(payload.error || "Payment Intent was not created.");
                }

                setPaymentStatus("Confirming card payment...", false);

                const paymentResult = await stripe.confirmCardPayment(payload.clientSecret, {
                    payment_method: {
                        card: cardElement,
                    },
                });

                if (paymentResult.error) {
                    throw new Error(paymentResult.error.message);
                }

                setPaymentStatus("Payment completed.", false);
            } catch (error) {
                setPaymentStatus(error.message, true);
                submitButton.disabled = false;
            }
        });
    } else {
        setPaymentStatus("Stripe Payment Intent is not configured.", true);
    }
}
