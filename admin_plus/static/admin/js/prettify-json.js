(function ($){

    function prettifyString(s) {
        var r_link = /^https?:\/\//;
        if (r_link.test(s)) {
                return '<a href="'+s+'" title="'+s+'">'+s.replace(r_link, '').split('/')[0]+'</a>';
            }
            return s;
    }

    function prettify(json) {
        if (typeof(json)=='undefined') {
            return '';
        }
        if (typeof(json)=='number') {
            return '<span class="value" data-json-number='+json+'>'+json+'</span>';
        }
        if (typeof(json)=="boolean") {
            var value = JSON.stringify(json);
            return '<span class="json-prettify-bool" data-json-bool="'+value+'">'+value+'</span>'
        }
        if (typeof(json)=="string") {
            return '<span class="value">'+prettifyString(json)+'</span>';
        } else
        if (typeof(json)=="object") {
            result = '<ul class="code">';
            for (var property in json) {
                result += '<li><span class="property">'+prettifyString(property)+': </span>'+prettify(json[property])+'</li>';
            }
            result += '</ul>';
            return result;
        } else
        if (json.isArray) {
            var l = json.length;
            result = '<ul class="code">';
            for (var i=0; i<l; i++) {
                result += '<li>'+prettify(json[i])+'</li>';
            }
            result += '</ul>';
            return result;
        }
        return "error";
    }


    $().ready(function() {
        $('.prettify-json').each(function(i) {

            var $this = $(this);

            if ($this.hasClass('already-prettified')) {
                /* already prettified... */
                return;
            }
            try {
                var json = $(this).html();
                var result = prettify(JSON.parse(json));
                $(this).parent().append('<div class="json-prettified">'+result+'</div>');
                $(this).hide().addClass('already-prettified');
            } catch(e) {
                /*sorry, could not parse it correctly!*/
            }
        })
    })
})(django.jQuery);