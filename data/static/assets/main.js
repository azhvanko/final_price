const defaultErrorMessage = 'An unexpected error occurred. Please try again later';
let isSubmitting = false;
let toastTimeout = null;

function showToast(toast, message, type = 'success') {
    if (toastTimeout) {
        clearTimeout(toastTimeout);
    }
    toast.textContent = message;
    toast.className = 'toast';
    toast.classList.add('show', type);
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show', type);
        toastTimeout = null;
    }, 3500);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function isInputDataValid(nameInput, phoneInput) {
    const name = nameInput.value.trim();
    const nameRegex = /^[\p{L} '’-]+$/u;
    if (name.length < 2 || name.length > 128 || !nameRegex.test(name)) {
        return { isValid: false, message: 'Invalid name. Please use letters and spaces only' };
    }
    const phone = phoneInput.value.trim();
    const phoneRegex = /^[\d ()+-]+$/;
    const phoneDigits = phone.replace(/\D/g, '');
    const hasValidPhoneChars = phoneRegex.test(phone);
    if (phoneDigits.length < 7 || phoneDigits.length > 15 || !hasValidPhoneChars) {
        return { isValid: false, message: 'Invalid phone number. Please use digits and standard symbols only' };
    }
    return { isValid: true, message: '' };
}

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

async function createOrder(orderData) {
    const MAX_RETRIES = 10;
    const RETRY_DELAY = 500;
    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        const response = await fetch('/api/orders/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData),
        });
        if (response.ok) {
            return response.json();
        }
        if (response.status >= 400 && response.status < 500) {
            const message = await getErrorMessage(response);
            throw new Error(message);
        }
        if (attempt < MAX_RETRIES) {
            await sleep(RETRY_DELAY);
        } else {
            const message = await getErrorMessage(response);
            throw new Error(message);
        }
    }
}

async function getOrderStatus(orderId) {
    const MAX_VERIFY_ATTEMPTS = 20;
    const VERIFY_DELAY = 250;
    for (let attempt = 1; attempt <= MAX_VERIFY_ATTEMPTS; attempt++) {
        const response = await fetch(`/api/orders/${orderId}/status`);
        if (response.ok) {
            const statusData = await response.json();
            if (['ACCEPTED', 'REJECTED', 'ERROR'].includes(statusData.status)) {
                return statusData;
            }
        } else if (response.status === 400) {
            const errorMessage = await getErrorMessage(response);
            throw new Error(errorMessage);
        }
        else if (response.status === 404) {
            throw new Error('Order verification failed: order not found');
        }
        if (attempt < MAX_VERIFY_ATTEMPTS) {
            await sleep(VERIFY_DELAY);
        }
    }
    throw new Error('Order processing timed out. Please try again later');
}


document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('order-form');
    const nameInput = document.getElementById('user-name');
    const phoneInput = document.getElementById('user-phone');
    const submitButton = document.getElementById('submit-button');
    const toast = document.getElementById('toast-notification');
    const validateForm = () => {
        const isNameEntered = nameInput.value.trim() !== '';
        const isPhoneEntered = phoneInput.value.trim() !== '';
        submitButton.disabled = !(isNameEntered && isPhoneEntered);
    };
    nameInput.addEventListener('input', validateForm);
    phoneInput.addEventListener('input', validateForm);
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (isSubmitting) return;
        isSubmitting = true;
        const validationResult = isInputDataValid(nameInput, phoneInput);
        if (!validationResult.isValid) {
            showToast(toast, validationResult.message, 'error');
            isSubmitting = false;
            return;
        }
        submitButton.disabled = true;
        submitButton.textContent = 'Sending...';
        try {
            const orderData = {
                user_name: nameInput.value.trim(),
                phone_number: phoneInput.value.trim(),
            };
            const createdOrderResponse = await createOrder(orderData);
            submitButton.textContent = 'Verifying...';
            const getOrderStatusResponse = await getOrderStatus(createdOrderResponse.id);
            const orderStatus = getOrderStatusResponse.status;
            const detailMessage = getOrderStatusResponse.detail;
            const isSuccess = getOrderStatusResponse.status === 'ACCEPTED';
            showToast(toast, getOrderStatusResponse.detail, isSuccess ? 'success' : 'error');
            form.reset();
        } catch (error) {
            showToast(toast, error.message, 'error');
            form.reset();
        } finally {
            isSubmitting = false;
            submitButton.textContent = 'Submit';
            validateForm();
        }
    });
});
