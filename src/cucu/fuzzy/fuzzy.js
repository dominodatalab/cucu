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
    jqCucu.extend(
        jqCucu.expr[ ":" ],
        {
            has_text: function(elem, index, match) {
                return (elem.textContent || elem.innerText || jqCucu(elem).text() || '').trim() === match[3].trim();
            },
            vis: function (elem) {
                return !(jqCucu(elem).is(":hidden") || jqCucu(elem).css("width") == "0px" || jqCucu(elem).css("height") == "0px" || jqCucu(elem).parents(":hidden").length);
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
     *   name              - name that identifies the element you are trying to find
     *   things            - array of CSS fragments that specify the kind of elements
     *                       you want to match on
     *   index             - which of the many matches to return
     *   direction         - the text to element direction to apply fuzzy in. Default
     *                       we apply right to left but for checkboxes or certain
     *                       languages this direction can be used to find things by
     *                       prioritizing matching from "left to right"
     *   name_within_thing - to determine if the name has to be within the web element
     */
    cucu.fuzzy_find = function(name,
                               things,
                               index=0,
                               direction=LEFT_TO_RIGHT,
                               name_within_thing=false) {
        var elements = [];
        var results = null;
        var attributes = ['aria-label', 'title', 'placeholder', 'value'];
        var matchers = ['has_text', 'contains'];

        name = name.replaceAll('"', '\\"')

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
                results = jqCucu(thing + ':vis:' + matcher + '("' + name + '")', document.body).toArray();
                if (cucu.debug) { console.log('<thing>name</thing>', results); }
                elements = elements.concat(results);

                // <thing attribute="name"></thing>
                for(var aIndex=0; aIndex < attributes.length; aIndex++) {
                    var attribute_name = attributes[aIndex];
                    if (matcher == 'has_text') {
                        results = jqCucu(thing + '[' + attribute_name + '="' + name + '"]:vis', document.body).toArray();
                        if (cucu.debug) { console.log('<thing attribute="name"></thing>', results); }
                    } else if (matcher == 'contains') {
                        results = jqCucu(thing + '[' + attribute_name + '*="' + name + '"]:vis', document.body).toArray();
                        if (cucu.debug) { console.log('<thing attribute*="name"></thing>', results); }
                    }
                    elements = elements.concat(results);
                }
            }

            /*
             * validate against the `value` attribute of the actual DOM object
             * as that has the value that may have changed from having written
             * a new value into an input which doesn't get reflected in the DOM.
             *
             * TODO: I think there may be a cleaner way to handle this but for
             *       now lets just add another loop in here.
             */
            for(var tIndex = 0; tIndex < things.length; tIndex++) {
                var thing = things[tIndex];

                // <thing value="name"></thing>
                if (matcher == 'has_text') {
                    results = jqCucu(thing + ':vis', document.body).filter(function(){
                        return this.value == name;
                    }).toArray();
                    if (cucu.debug) { console.log('<thing value="name"></thing>', results); }
                } else if (matcher == 'contains') {
                    results = jqCucu(thing + ':vis', document.body).filter(function(){
                        return this.value !== undefined && String(this.value).indexOf(name) != -1;
                    }).toArray();
                    if (cucu.debug) { console.log('<thing value*="name"></thing>', results); }
                }
                elements = elements.concat(results);
            }

            /*
             * element labeled by another using the for/id attributes
             */
            var labels = jqCucu('*[for]:vis:' + matcher + '("' + name + '")', document.body).toArray();
            for(var tIndex = 0; tIndex < things.length; tIndex++) {
                var thing = things[tIndex];
                results = [];

                /*
                 * <* for=...>name</*>...<thing id=...></thing>
                 */
                for(var lIndex=0; lIndex < labels.length; lIndex++) {
                    var label = labels[lIndex];
                    var id = label.getAttribute('for');
                    results = jqCucu(thing + '[id="' + id + '"]:vis', document.body).toArray();
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
                results = jqCucu('*:vis:' + matcher + '("' + name + '")', document.body).parents(thing).toArray();
                if (cucu.debug) { console.log('<thing><*>...name...</*></thing>', results); }
                elements = elements.concat(results);

                // <thing><* attribute="name"></*></thing>
                for(var aIndex=0; aIndex < attributes.length; aIndex++) {
                    var attribute_name = attributes[aIndex];
                    results = jqCucu('*:vis[' + attribute_name + '="' + name + '"]', document.body).parents(thing).toArray();
                    if (cucu.debug) { console.log('<thing><* attibute="name"></*></thing>', results); }
                    elements = elements.concat(results);
                }
            }

            // if the name has to be within the element, the following rules are not considered
            if (name_within_thing) {
                continue;
            }

            // element labeled with direct previous sibling
            if (direction === LEFT_TO_RIGHT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    // <*>name</*><thing/>
                    results = jqCucu('*:vis:' + matcher + '("' + name + '")', document.body).next(thing + ':vis').toArray();
                    if (cucu.debug) { console.log('<*>name</*><thing/>', results); }
                    elements = elements.concat(results);
                }
            }

            // element labeled with direct next sibling
            if (direction === RIGHT_TO_LEFT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    // <thing/><*>name</*>
                    results = jqCucu('*:vis:' + matcher + '("' + name + '")', document.body).prev(thing).toArray();
                    if (cucu.debug) { console.log('<thing/><*>name</*>', results); }
                    elements = elements.concat(results);
                }
            }

            /*
             * element labeled by a text sibling
             */
            for(var tIndex = 0; tIndex < things.length; tIndex++) {
                var thing = things[tIndex];

                /*
                 * <*><thing></thing>name</*>
                 */
                results = jqCucu('*:vis:' + matcher + '("' + name + '")', document.body).children(thing + ':vis').toArray();
                if (cucu.debug) { console.log('<*><thing></thing>name</*>', results); }
                elements = elements.concat(results);
            }

            // element labeled with any previous sibling
            if (direction === LEFT_TO_RIGHT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    // <*>name</*>...<thing>...
                    results = jqCucu('*:vis:' + matcher + '("' + name + '")', document.body).nextAll(thing + ':vis').toArray();
                    if (cucu.debug) { console.log('<*>name</*>...<thing>...', results); }
                    elements = elements.concat(results);

                    // <...><*>name</*></...>...<...><thing></...>
                    // XXX: this rule is horribly complicated and I'd rather see it gone
                    //      basically: common great grandpranet
                    results = jqCucu('*:vis:' + matcher + '("' + name + '")', document.body).nextAll().find(thing + ':vis').toArray();
                    if (cucu.debug) { console.log('<...><*>name</*></...>...<...><thing></...>', results); }
                    elements = elements.concat(results);
                }
            }

            // element labeled with any next sibling
            if (direction === RIGHT_TO_LEFT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    // next siblings: <thing>...<*>name</*>...
                    results = jqCucu('*:vis:' + matcher + '("' + name + '")', document.body).prevAll(thing).toArray();
                    if (cucu.debug) { console.log('<thing>...<*>name</*>...', results); }
                    elements = elements.concat(results);

                    // <...><thing></...>...<...><*>name</*></...>
                    // XXX: this rule is horribly complicated and I'd rather see it gone
                    results = jqCucu('*:vis:' + matcher + '("' + name + '")', document.body).prevAll().find(thing + ':vis').toArray();
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
