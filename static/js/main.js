// Custom JavaScript for Promo Bot Admin Panel

$(document).ready(function() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirm before dangerous actions
    $('.btn-danger').click(function(e) {
        if (!confirm('Haqiqatan ham davom etmoqchimisiz?')) {
            e.preventDefault();
        }
    });

    // Table row hover effect
    $('table tbody tr').hover(
        function() {
            $(this).addClass('table-active');
        },
        function() {
            $(this).removeClass('table-active');
        }
    );

    // Copy code to clipboard
    $('code').click(function() {
        var $temp = $("<input>");
        $("body").append($temp);
        $temp.val($(this).text()).select();
        document.execCommand("copy");
        $temp.remove();

        // Show toast notification
        showToast('Kod nusxalandi!');
    });

    // Character counter for textarea
    $('textarea').on('input', function() {
        var maxLength = $(this).attr('maxlength');
        if (maxLength) {
            var currentLength = $(this).val().length;
            var remaining = maxLength - currentLength;

            if (!$(this).next('.char-counter').length) {
                $(this).after('<div class="char-counter text-muted small"></div>');
            }

            $(this).next('.char-counter').text(remaining + ' belgi qoldi');
        }
    });

    // File input preview
    $('input[type="file"]').change(function() {
        var fileName = $(this).val().split('\\').pop();
        $(this).next('.custom-file-label').text(fileName || 'Fayl tanlang');
    });

    // Loading state for forms
    $('form').on('submit', function() {
        var $submitBtn = $(this).find('button[type="submit"]');
        $submitBtn.data('original-text', $submitBtn.html());
        $submitBtn.prop('disabled', true)
            .html('<span class="spinner-border spinner-border-sm me-2"></span>Yuklanmoqda...');
    });

    // Reset form button states on page load (for back button)
    $('button[type="submit"]').each(function() {
        var originalText = $(this).data('original-text');
        if (originalText) {
            $(this).prop('disabled', false).html(originalText);
        }
    });
});

// Toast notification function
function showToast(message, type = 'success') {
    var toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    var $toast = $(toastHtml);
    $('body').append($toast);

    var toast = new bootstrap.Toast($toast[0]);
    toast.show();

    $toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// AJAX form submission (optional enhancement)
function submitFormAjax(form, successCallback) {
    var formData = new FormData(form);

    $.ajax({
        url: $(form).attr('action') || window.location.href,
        type: $(form).attr('method') || 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (successCallback) {
                successCallback(response);
            } else {
                showToast('Muvaffaqiyatli bajarildi!');
            }
        },
        error: function(xhr, status, error) {
            showToast('Xatolik yuz berdi: ' + error, 'danger');
        },
        complete: function() {
            // Reset submit button
            var $submitBtn = $(form).find('button[type="submit"]');
            var originalText = $submitBtn.data('original-text');
            if (originalText) {
                $submitBtn.prop('disabled', false).html(originalText);
            }
        }
    });
}