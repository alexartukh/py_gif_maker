jQuery(function() {
    jQuery("#submit_button").click(function(e) {
        let t = jQuery("textarea[name=t]").val();
        let user = jQuery("input[name=user]").val();
        let template = jQuery("select[name=template]").val();

        jQuery.ajax({
            url: '/anno',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ t: t, user: user, template: template }), 
        })
        .done(function(data) {
            // data type of the result may be different
            jQuery('#result_text').html('');
            jQuery('#result_image').attr('src', '');

            if (! data.error) {
                if (data.result_type == 1) {
                    jQuery('#result_text').html(data.result);
                }
                if (data.result_type == 2) {
                    jQuery('#result_image').attr('src', data.result);
                }
            }
            
            console.log(data);
        });
    })

    
});