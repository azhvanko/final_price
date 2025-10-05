document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('order-form');
    const nameInput = document.getElementById('user-name');
    const phoneInput = document.getElementById('user-phone');
    const submitButton = document.getElementById('submit-button');
    const toast = document.getElementById('toast-notification');

    const defaultErrorMessage = 'An unexpected error occurred. Please try again later';

    const validateForm = () => {
        const isNameEntered = nameInput.value.trim() !== '';
        const isPhoneEntered = phoneInput.value.trim() !== '';
        submitButton.disabled = !(isNameEntered && isPhoneEntered);
    };

    function isInputDataValid() {
        const name = nameInput.value.trim();
        if (name.length < 2 || name.length > 128 || !/^[a-zA-Zа-яА-ЯёЁ\s'’‑-]*$/.test(name)) {
            return { isValid: false, message: 'Invalid name. Please use letters and spaces' };
        }
        const phone = phoneInput.value.trim();
        const phoneDigits = phone.replace(/\D/g, '');
        const hasValidPhoneChars = /^[\d\s()+-]*$/.test(phone);
        if (phoneDigits.length < 7 || phoneDigits.length > 24 || !hasValidPhoneChars) {
            return { isValid: false, message: 'Invalid phone number' };
        }
        return { isValid: true, message: '' };
    }

    nameInput.addEventListener('input', validateForm);
    phoneInput.addEventListener('input', validateForm);

    async function getErrorMessage(response) {
        let message = defaultErrorMessage;
        try {
            const errorData = await response.json();
            if (errorData && errorData.detail) {
                message = errorData.detail;
            }
        } catch (e) {}
        return message;
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const validationResult = isInputDataValid();
        if (!validationResult.isValid) {
            showToast(validationResult.message, 'error');
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = 'Sending...';

        const orderData = {
            user_name: nameInput.value.trim(),
            phone_number: phoneInput.value.trim(),
        };

        try {
            const MAX_RETRIES = 5;
            const RETRY_DELAY = 2000;
            let createOrderResponse;
            for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
                createOrderResponse = await fetch('/api/orders/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(orderData),
                });
                if (createOrderResponse.ok) {
                    break;
                }
                if (createOrderResponse.status >= 400 && createOrderResponse.status < 500) {
                    const errorMessage = await getErrorMessage(createOrderResponse);
                    form.reset();
                    throw new Error(errorMessage);
                }
                if (createOrderResponse.status >= 500) {
                    if (attempt < MAX_RETRIES) {
                        await sleep(RETRY_DELAY);
                        continue;
                    } else {
                        const finalMessage = await getErrorMessage(createOrderResponse);
                        form.reset();
                        throw new Error(finalMessage);
                    }
                }
            }

            const createOrderResponseData = await createOrderResponse.json();
            const orderId = createOrderResponseData.id;

            submitButton.textContent = 'Verifying...';

            const MAX_VERIFY_ATTEMPTS = 8;
            const VERIFY_DELAY = 1500;

            for (let attempt = 1; attempt <= MAX_VERIFY_ATTEMPTS; attempt++) {
                const verifyResponse = await fetch(`/api/orders/${orderId}/status`);
                if (verifyResponse.ok) {
                    const statusData = await verifyResponse.json();
                    const internalStatus = statusData.status;
                    const detailMessage = statusData.detail;
                    if (internalStatus === 'ACCEPTED') {
                        showToast(detailMessage, 'success');
                        form.reset();
                        return;
                    }
                    if (internalStatus === 'REJECTED' || internalStatus === 'ERROR') {
                        showToast(detailMessage, 'error');
                        form.reset();
                        return;
                    }
                    if (internalStatus === 'PROCESSING') {
                        if (attempt < MAX_VERIFY_ATTEMPTS) {
                            await sleep(VERIFY_DELAY);
                            continue;
                        } else {
                            throw new Error('Order processing timed out. Please try again later');
                        }
                    }
                }
                else if (verifyResponse.status === 400) {
                    const errorMessage = await getErrorMessage(verifyResponse);
                    throw new Error(errorMessage);
                }
                else if (verifyResponse.status === 404) {
                    throw new Error('Order verification failed: order not found');
                }
                else if (verifyResponse.status >= 500) {
                    if (attempt < MAX_VERIFY_ATTEMPTS) {
                        await sleep(VERIFY_DELAY);
                        continue;
                    } else {
                        throw new Error('Verification failed: server is not responding');
                    }
                }
                else {
                    throw new Error(`Verification failed`);
                }
            }
        } catch (error) {
            showToast(defaultErrorMessage, 'error');
        } finally {
            submitButton.textContent = 'Submit';
            validateForm();
        }
    });

    function showToast(message, type = 'success') {
        toast.textContent = message;
        toast.className = `toast show ${type}`;
        setTimeout(() => {toast.className = 'toast'}, 3500);
    }
});
