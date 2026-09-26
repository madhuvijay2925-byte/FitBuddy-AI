function confirmDelete() {
    return confirm(
        "Are you sure you want to delete this user?"
    );
}


document.addEventListener(
    "submit",
    function (event) {

        const button =
            event.target.querySelector(
                "button[type='submit']"
            );

        if (button) {
            button.disabled = true;
            button.innerText = "Working...";
        }

    }
);