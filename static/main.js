jQuery(function() {
    jQuery("#submit_button").click(function(e) {
        let t = jQuery("input[name=t]").val();
        let login = jQuery("input[name=login]").val();
        let password = jQuery("input[name=password]").val();
        let template = jQuery("select[name=template]").val();

        let d = { t: t, login: login, password: password, template: template };
        
        console.log("Sending request");
        console.log(d);

        jQuery.ajax({
            url: '/anno',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(d), 
        })
        .done(function(data) {
            jQuery('#result_text').html('');
            jQuery('#result_image').attr('src', '');

            console.log("Receiving response");
            console.log(data);
            
            // print JSON response in any case
            jQuery('#result_text').html( '<pre>' + JSON.stringify(data, null, 2) + '</pre>' )

            if (! data.error) {
                jQuery('#result_image').attr('src', data.result);

                // use black color font for a normal response
                jQuery('#result_text').css('color', 'black');
            }
            else {
                // use red color font for an error response
                jQuery('#result_text').css('color', 'red');
            }
        });
    });
});