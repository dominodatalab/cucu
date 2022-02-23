(function(){
    window.cucu = {
        debug: false
    };

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

    // this matches the class Direction in  cucu/fuzzy/core.py
    const LEFT_TO_RIGHT = 1;
    const RIGHT_TO_LEFT = 2;

    /*
     * find an element by applying the fuzzy finding rules when given the name
     * that identifies the element on screen and a list of possible `things` that
     * are CSS expression fragments like so:
     *
     *     tag_name[attribute expression]
     *
     * That identify the kind of element you're trying to find, such as a button,
     * input[type='button'], etc.
     *
     * parameters:
     *   name           - name that identifies the element you are trying to find
     *   things         - array of CSS fragments that specify the kind of elements
     *                    you want to match on
     *   index          - which of the many matches to return
     *   direction      - the text to element direction to apply fuzzy in. Default
     *                    we apply right to left but for checkboxes or certain
     *                    languages this direction can be used to find things by
     *                    prioritizing matching from "left to right"
     */
    cucu.fuzzy_find = function(name,
                               things,
                               index=0,
                               direction=LEFT_TO_RIGHT) {
        var elements = [];
        var results = null;
        var attributes = ['aria-label', 'title', 'placeholder', 'value'];
        var matchers = ['has_text', 'contains'];

        name = name.replaceAll('"', '\\\"')

        /*
         * try to match on exact text but ultimately fall back to matching on
         * the elements text that contains the string we're searching for
         */
        for(var mIndex=0; mIndex < matchers.length; mIndex++) {
            var matcher = matchers[mIndex];

            /*
             * element labeled in itself or by its own attributes
             */
            for(var tIndex = 0; tIndex < things.length; tIndex++) {
                var thing = things[tIndex];

                /*
                 * <thing>name</thing>
                 */
                results = jQuery(thing + ':vis:' + matcher + '("' + name + '")').toArray();
                if (cucu.debug) { console.log('<thing>name</thing>', results); }
                elements = elements.concat(results);

                // <thing attribute="name"></thing>
                for(var aIndex=0; aIndex < attributes.length; aIndex++) {
                    var attribute_name = attributes[aIndex];
                    results = jQuery(thing + '[' + attribute_name + '="' + name + '"]:vis').toArray();
                    if (cucu.debug) { console.log('<thing attibute="name"></thing>', results); }
                    elements = elements.concat(results);
                }
            }

            /*
             * element labeled by another using the for/id attributes
             */
            var labels = jQuery('*[for]:vis:' + matcher + '("' + name + '")').toArray();
            for(var tIndex = 0; tIndex < things.length; tIndex++) {
                var thing = things[tIndex];
                results = [];

                /*
                 * <* for=...>name</*>...<thing id=...></thing>
                 */
                for(var lIndex=0; lIndex < labels.length; lIndex++) {
                    var label = labels[lIndex];
                    var id = label.getAttribute('for');
                    results = jQuery(thing + '[id="' + id + '"]:vis').toArray();
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
                results = jQuery('*:' + matcher + '("' + name + '")').parents(thing).toArray();
                if (cucu.debug) { console.log('<thing><*>...name...</*></thing>', results); }
                elements = elements.concat(results);
            }

            /*
             * element labeled by previous sibling
             */
            if (direction === LEFT_TO_RIGHT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    // <*>name</*><thing/>
                    results = jQuery('*:vis:' + matcher + '("' + name + '")').next(thing + ':vis').toArray();
                    if (cucu.debug) { console.log('<*>name</*><thing/>', results); }
                    elements = elements.concat(results);

                    // <*>name</*>...<thing>...
                    results = jQuery('*:vis:' + matcher + '("' + name + '")').nextAll(thing + ':vis').toArray();
                    if (cucu.debug) { console.log('<*>name</*>...<thing>...', results); }
                    elements = elements.concat(results);

                    // <...><*>name</*></...>...<...><thing></...>
                    // XXX: this rule is horribly complicated and I'd rather see it gone
                    //      basically: common great grandpranet
                    results = jQuery('*:vis:' + matcher + '("' + name + '")').nextAll().find(thing + ':vis').toArray();
                    if (cucu.debug) { console.log('<...><*>name</*></...>...<...><thing></...>', results); }
                    elements = elements.concat(results);
                }
            }

            // element labeled with next sibling
            if (direction === RIGHT_TO_LEFT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    // <thing/> <*>name</*>
                    results = jQuery('*:vis:' + matcher + '("' + name + '")').prev(thing).toArray();
                    if (cucu.debug) { console.log('<thing/><*>name</*>', results); }
                    elements = elements.concat(results);

                    // next siblings: <thing>...<*>name</*>...
                    results = jQuery('*:vis:' + matcher + '("' + name + '")').prevAll(thing).toArray();
                    if (cucu.debug) { console.log('<thing>...<*>name</*>...', results); }
                    elements = elements.concat(results);

                    // <...><thing></...>...<...><*>name</*></...>
                    // XXX: this rule is horribly complicated and I'd rather see it gone
                    results = jQuery('*:vis:' + matcher + '("' + name + '")').prevAll().find(thing + ':vis').toArray();
                    if (cucu.debug) { console.log('<...><thin></...>...<...><*>name</*></...>', results); }
                    elements = elements.concat(results);
                }
            }
        }

        if (cucu.debug) {
            console.log(elements);
        }
        return elements[index];
    };
})();
