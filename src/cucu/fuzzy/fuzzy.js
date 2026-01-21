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
                               name_within_thing=false,
                               insert_label=false) {
        var elements = [];
        var results = null;
        var attributes = ['aria-label', 'title', 'placeholder', 'value'];
        var matchers = ['has_text', 'contains'];

        name = name.replaceAll('"', '\\"');

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

                var nameInTagContentLabel = `<${thing}>${name}</${thing}>`;
                var nameInTagContentJq = `${thing}:vis:${matcher}("${name}")`;
                results = jqCucu(nameInTagContentJq, document.body).toArray();
                if (cucu.debug) { console.log(nameInTagContentLabel, results); }
                elements = elements.concat(results.map(x => ({element: x, label: nameInTagContentLabel})));

                for(var aIndex=0; aIndex < attributes.length; aIndex++) {
                    var attribute_name = attributes[aIndex];
                    var nameIsAttributeLabel = `<${thing} attribute="${attribute_name}"></${thing}>`;
                    if (matcher == 'has_text') {
                        var nameIsAttributeJq = `${thing}[${attribute_name}="${name}"]:vis`;
                        results = jqCucu(nameIsAttributeJq, document.body).toArray();
                        if (cucu.debug) { console.log(nameIsAttributeLabel, results); }
                    } else if (matcher == 'contains') {
                        var nameInAttributeJq = `${thing}[${attribute_name}*="${name}"]:vis`;
                        results = jqCucu(nameInAttributeJq, document.body).toArray();
                        if (cucu.debug) { console.log(nameIsAttributeLabel, results); }
                    }
                    elements = elements.concat(results.map(x => ({element: x, label: nameIsAttributeLabel})));
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

                if (matcher == 'has_text') {
                    var nameIsValueLabel = `${thing} value="${name}"></${thing}>`;
                    var nameIsValueJq = `${thing}:vis`;
                    results = jqCucu(nameInValueJq, document.body).filter(function(){
                        return this.value == name;
                    }).toArray();
                    if (cucu.debug) { console.log(nameIsValueLabel, results); }
                } else if (matcher == 'contains') {
                    var nameInValueLabel = `${thing} value*="${name}"></${thing}>`;
                    var nameInValueJq = `${thing}:vis`;
                    results = jqCucu(nameInValueJq, document.body).filter(function(){
                        return this.value !== undefined && String(this.value).indexOf(name) != -1;
                    }).toArray();
                    if (cucu.debug) { console.log(nameInValueLabel, results); }
                }
                elements = elements.concat(results.map(x => ({element: x, label: nameInValueLabel})));
            }

            /*
             * element labeled by another using the for/id attributes
             */
            var labelForNameJq = `*[for]:vis:${matcher}("${name}")`
            var labels = jqCucu(labelForNameJq, document.body).toArray();
            for(var tIndex = 0; tIndex < things.length; tIndex++) {
                var thing = things[tIndex];
                results = [];

                var labelForNameLabel = `<* for=...>${name}</*>...<${thing} id=...></${thing}>`;
                for(var lIndex=0; lIndex < labels.length; lIndex++) {
                    var label = labels[lIndex];
                    var id = label.getAttribute('for');
                    var idMatchesForLabelJq = `${thing}[id="${id}"]:vis`;
                    results = jqCucu(idMatchesForLabelJq, document.body).toArray();

                    if (cucu.debug) { console.log(labelForNameLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: labelForNameLabel})));
                }
            }

            /*
             * element labeled by a nested child
             */
            for(var tIndex = 0; tIndex < things.length; tIndex++) {
                var thing = things[tIndex];

                var nameInNestedChildLabel = `<${thing}><*>...${name}...</*></${thing}>`;
                results = jqCucu('*:vis:' + matcher + '("' + name + '")', document.body).parents(thing).toArray();
                if (cucu.debug) { console.log(nameInNestedChildLabel, results); }
                elements = elements.concat(results.map(x => ({element: x, label: nameInNestedChildLabel})));

                for(var aIndex=0; aIndex < attributes.length; aIndex++) {
                    var attribute_name = attributes[aIndex];
                    var innerNestedElementsLabel = `<${thing}><* ${attribute_name}="${name}"></*></${thing}>`;
                    results = jqCucu(`*:vis[${attribute_name}="${name}"]`, document.body).parents(thing).toArray();
                    if (cucu.debug) { console.log(innerNestedElementsLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: innerNestedElementsLabel})));
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

                    var nameIsPreviousSiblingLabel = `<*>${name}</*><${thing}/>`;
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).next(thing + ':vis').toArray();
                    if (cucu.debug) { console.log(nameIsPreviousSiblingLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: nameIsPreviousSiblingLabel})));
                }
            }

            // element labeled with direct next sibling
            if (direction === RIGHT_TO_LEFT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    var nameIsNextSiblingLabel = `<${thing}/><*>${name}</*>`;
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).prev(thing).toArray();
                    if (cucu.debug) { console.log(nameIsNextSiblingLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: nameIsNextSiblingLabel})));
                }
            }

            /*
             * element labeled by a text sibling
             */
            for(var tIndex = 0; tIndex < things.length; tIndex++) {
                var thing = things[tIndex];

                var nameIsTextSiblingLabel = `<*><${thing}></${thing}>${name}</*>`;
                results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).children(thing + ':vis').toArray();
                if (cucu.debug) { console.log(nameIsTextSiblingLabel, results); }
                elements = elements.concat(results.map(x => ({element: x, label: nameIsTextSiblingLabel})));
            }

            // element labeled with any previous sibling
            if (direction === LEFT_TO_RIGHT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    var leftToRightLabel = `<*>${name}</*>...<${thing}>...`;
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).nextAll(thing + ':vis').toArray();
                    if (cucu.debug) { console.log(leftToRightLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: leftToRightLabel})));

                    var leftToRightGrandpaLabel = `<...><*>${name}</*></...>...<...><${thing}></...>`;
                    // XXX: this rule is horribly complicated and I'd rather see it gone
                    //      basically: common great grandpranet
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).nextAll().find(thing + ':vis').toArray();
                    if (cucu.debug) { console.log(leftToRightGrandpaLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: leftToRightGrandpaLabel})));
                }
            }

            // element labeled with any next sibling
            if (direction === RIGHT_TO_LEFT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    var rightToLeftLabel = `<${thing}>...<*>${name}</*>...`;
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).prevAll(thing).toArray();
                    if (cucu.debug) { console.log(rightToLeftLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: rightToLeftLabel})));

                    var rightToLeftGrandpaLabel = `<...><${thing}></...>...<...><*>${name}</*></...>`;
                    // XXX: this rule is horribly complicated and I'd rather see it gone
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).prevAll().find(thing + ':vis').toArray();
                    if (cucu.debug) { console.log(rightToLeftGrandpaLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: rightToLeftGrandpaLabel})));
                }
            }
        }

        // deduplicate elements by element identity, keeping order
        var deduped_elements = [];
        var seen_elements = [];
        for (var i = 0; i < elements.length; i++) {
            if (seen_elements.indexOf(elements[i].element) === -1) {
                seen_elements.push(elements[i].element);
                deduped_elements.push(elements[i]);
            }
        }
        elements = deduped_elements;

        if ((elements.length > 1 && index > 0) || cucu.debug) {
            console.debug(`fuzzy_find: multiple (${elements.length}) matches, returning index ${index}.\n`);
            for (var i = 0; i < elements.length; i++) {
                const rect = elements[i].element.getBoundingClientRect();
                console.debug(`  [${i}]: ${(elements[i].element.textContent || elements[i].element.innerText || jqCucu(elements[i].element).text() || '').trim()} at (${rect.x}, ${rect.y})\n`);
            }
        } else if (elements.length > 0) {
            let rect = elements[0].element.getBoundingClientRect();
            console.debug(`fuzzy_find: selected first element: ${(elements[0].element.textContent || elements[0].element.innerText || jqCucu(elements[0].element).text() || '').trim()} at (${rect.x}, ${rect.y})`);
        }

        if (elements.length > 0 && insert_label) {
            return [elements[index].element, elements[index].label];
        }
        return elements[index];
    };
})();
