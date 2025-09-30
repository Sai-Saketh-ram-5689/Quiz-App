$(document).ready(function () {
    // Generic form validation on submit
    $('form[novalidate]').on('submit', function (e) {
        const form = $(this)[0];
        let valid = true;
        $(form).find('[required]').each(function () {
            if (!this.value || ($(this).is(':radio') && !$('input[name="' + this.name + '"]:checked').length)) {
                $(this).addClass('is-invalid');
                valid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });

        // Special treatment for radio groups
        $(form).find('input[type=radio]').each(function () {
            const name = $(this).attr('name');
            if ($('input[name="' + name + '"]:required').length && !$('input[name="' + name + '"]:checked').length) {
                // mark the first radio in the group as invalid visually
                $('input[name="' + name + '"]').closest('label').addClass('is-invalid');
                valid = false;
            }
        });

        if (!valid) {
            e.preventDefault();
            e.stopPropagation();
        }
    });

    // Remove invalid class on input
    $(document).on('input change', 'input, select, textarea', function () {
        if (this.value) $(this).removeClass('is-invalid');
    });

    // Confirm finish adding questions
    $(document).on('click', 'button[name=finish]', function (e) {
        const ok = confirm('Are you sure you want to finish adding questions and return to the dashboard?');
        if (!ok) e.preventDefault();
    });
});
