(function(){
    if (!window.cucu) {
        window.cucu = {
            debug: false
        };
    }

    /*
     * custom jquery matchers:
     *
     *
     *  has_text - matches an element with the exact text provided.
     *
     *  vis      - matches an element that is visible and has at least
     *             one visible parent.
     *
     */
    jQuery.extend(
        jQuery.expr[ ":" ],
        {
            has_text: function(elem, index, match) {
                return (elem.textContent || elem.innerText || jQuery(elem).text() || '') === match[3].trim();
            },
            vis: function (elem) {
                return !(jQuery(elem).is(":hidden") || jQuery(elem).parents(":hidden").length);
            }
        }
    );

    cucu.a11y_find = function(name, things, attributes, index=0) {
        var elements = [];
        var results = null;
        name = name.replaceAll('"', '\\"')

        /*
         * element labeled in itself or by its own attributes
         */
        for(var tIndex = 0; tIndex < things.length; tIndex++) {
            var thing = things[tIndex];

            /*
             * <thing>name</thing>
             */
            results = jQuery(thing + ':vis:has_text("' + name + '")', document.body).toArray();
            if (cucu.debug) { console.log('<thing>name</thing>', results); }
            elements = elements.concat(results);

            // <thing attribute="name"></thing>
            for(var aIndex=0; aIndex < attributes.length; aIndex++) {
                var attribute_name = attributes[aIndex];
                results = jQuery(thing + '[' + attribute_name + '="' + name + '"]:vis', document.body).toArray();
                if (cucu.debug) { console.log('<thing attibute="name"></thing>', results); }
                elements = elements.concat(results);
            }
        }

        /*
         * element labeled by another using aria-labelledby
         */
        var labels = jQuery('*[id]:vis:has_text("' + name + '")', document.body).toArray();
        for(var tIndex = 0; tIndex < things.length; tIndex++) {
            var thing = things[tIndex];
            results = [];

            /*
             * <* aria-labelledby=...>name</*>...<thing id=...></thing>
             */
            for(var lIndex=0; lIndex < labels.length; lIndex++) {
                var label = labels[lIndex];
                var id = label.getAttribute('id');
                results = jQuery(thing + '[aria-labelledby="' + id + '"]:vis', document.body).toArray();
                if (cucu.debug) { console.log('<* aria-labelledby=...>name</*>...<thing id=...></thing>', results); }
                elements = elements.concat(results);
            }
        }

        /*
         * element labeled by another using the for/id attributes
         */
        var labels = jQuery('*[for]:vis:has_text("' + name + '")', document.body).toArray();
        for(var tIndex = 0; tIndex < things.length; tIndex++) {
            var thing = things[tIndex];
            results = [];

            /*
             * <* for=...>name</*>...<thing id=...></thing>
             */
            for(var lIndex=0; lIndex < labels.length; lIndex++) {
                var label = labels[lIndex];
                var id = label.getAttribute('for');
                results = jQuery(thing + '[id="' + id + '"]:vis', document.body).toArray();
                if (cucu.debug) { console.log('<* for=...>name</*>...<thing id=...></thing>', results); }
                elements = elements.concat(results);
            }
        }

        /*
         * element labeled by a nested child
         */
        for(var tIndex = 0; tIndex < things.length; tIndex++) {
            var thing = things[tIndex];

            /*
             * <thing><*>...name...</*></thing>
             */
            results = jQuery('*:vis:has_text("' + name + '")', document.body).parents(thing).toArray();
            if (cucu.debug) { console.log('<thing><*>...name...</*></thing>', results); }
            elements = elements.concat(results);

            // <thing><* attribute="name"></*></thing>
            for(var aIndex=0; aIndex < attributes.length; aIndex++) {
                var attribute_name = attributes[aIndex];
                results = jQuery('*:vis[' + attribute_name + '="' + name + '"]', document.body).parents(thing).toArray();
                if (cucu.debug) { console.log('<thing><* attibute="name"></*></thing>', results); }
                elements = elements.concat(results);
            }
        }

        if (cucu.debug) {
            console.log(elements);
        }
        return elements[index];
    };
})();
