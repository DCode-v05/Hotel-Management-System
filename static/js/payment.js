function openPaymentModal(roomNumber, pricePerDay) {
    console.log("openPaymentModal triggered for room:", roomNumber);
    console.log("openPaymentModal triggered for prize:", pricePerDay);

    const modal = document.getElementById("payment-modal");
    const totalPriceElement = document.getElementById("total-price");

    if (!modal || !totalPriceElement) {
        console.error("Payment modal or total price element not found in DOM!");
        return;
    }

    const checkInInput = document.getElementById(`check_in_${roomNumber}`);
    const checkOutInput = document.getElementById(`check_out_${roomNumber}`);

    if (!checkInInput || !checkOutInput) {
        alert("Please select check-in and check-out dates first.");
        return;
    }

    const checkInDate = new Date(checkInInput.value);
    const checkOutDate = new Date(checkOutInput.value);

    if (isNaN(checkInDate.getTime()) || isNaN(checkOutDate.getTime())) {
        alert("Please enter valid check-in and check-out dates.");
        return;
    }

    const days = (checkOutDate - checkInDate) / (1000 * 60 * 60 * 24);
    if (days < 1) {
        alert("Minimum stay is 1 day.");
        return;
    }

    totalPriceElement.innerText = (days * pricePerDay).toFixed(2);
    modal.style.display = "flex";
}

function closePaymentModal() {
    document.getElementById("payment-modal").style.display = "none";
}

function confirmOnlinePayment() {
    alert("Online payment is currently unavailable.");
}

function confirmCashPayment() {
    alert("Booking confirmed with Cash on Delivery!");
    document.querySelector(".booking-form").submit();
}
