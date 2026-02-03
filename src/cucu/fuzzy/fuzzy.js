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

    // Helpers and relevance scoring promoted to cucu.relevance
    function getImmediateText(el) {
        var parts = [];
        var nodes = el.childNodes || [];
        for (var i = 0; i < nodes.length; i++) {
            var n = nodes[i];
            if (n.nodeType === 3) {
                parts.push((n.nodeValue || '').trim());
            }
        }
        return parts.join(' ').trim();
    }

    function getFullText(el) {
        return (el.textContent || el.innerText || jqCucu(el).text() || '').replace(/\n/g, ' ').trim();
    }

    function getAttr(el, name) {
        if (name === 'class') {
            return (el.className || '').toString();
        }
        return (el.getAttribute && el.getAttribute(name)) || '';
    }

    const WEIGHTS = {
        area: {
            immediate: 300,
            attribute: 200,
            fulltext: 100
        },
        match: {
            exact: 200,
            substring: 50
        },
        attrSub: {
            'aria-label': 34,
            'id': 23,
            'class': 12
        },
        emptyText: 11
    };


    /*
     * Relevance scoring (ordering)
     *
     * Case-sensitive matching. Higher scores rank first. After scoring, we
     * deduplicate and sort by score desc, then by original discovery order
     * (`pass`) asc as a tiebreaker. The `index` returned by fuzzy_find is
     * the Nth best-ranked element after this sort.
     *
     * Area priority (highest → lowest):
     *   1) Immediate text content (direct TEXT_NODE children only)
     *   2) Attribute content with sub-weights (aria-label > id > class; others default)
     *   3) Full text content (includes children)
     *
     * Within each area, exact match outranks substring match.
     *
     * Empty text fallback: if nothing matches and the element has empty
     * full text, a small default score is applied so empty-but-possibly
     * relevant nodes are not entirely discarded.
     */
    cucu.relevance = function(el, query, immediateOverride) {
        function includes(hay, needle) {
            if (!hay) return false;
            return hay.indexOf(needle) !== -1;
        }

        function equals(hay, needle) {
            if (!hay) return false;
            return hay.trim() === needle.trim();
        }

        var best = 0;
        var higherPriorityMatchFound = false;

        var imm = immediateOverride || getImmediateText(el);
        if (equals(imm, query)) {
            best = Math.max(best, WEIGHTS.area.immediate + WEIGHTS.match.exact);
            higherPriorityMatchFound = true;
        } else if (includes(imm, query)) {
            best = Math.max(best, WEIGHTS.area.immediate + WEIGHTS.match.substring);
            higherPriorityMatchFound = true;
        }

        var attrNames = ['aria-label', 'id', 'class', 'title', 'placeholder', 'value'];
        for (var a = 0; a < attrNames.length; a++) {
            var an = attrNames[a];
            var av = getAttr(el, an) || '';
            if (!av) continue;
            var sub = WEIGHTS.attrSub[an] || 0;
            if (equals(av, query)) {
                best = Math.max(best, WEIGHTS.area.attribute + WEIGHTS.match.exact + sub);
                higherPriorityMatchFound = true;
            } else if (includes(av, query)) {
                best = Math.max(best, WEIGHTS.area.attribute + WEIGHTS.match.substring + sub);
                higherPriorityMatchFound = true;
            }
        }

        var ft = getFullText(el);
        if (equals(ft, query)) {
            // Only promote exact full text matches to immediate weight when no higher priority matches found
            var fullTextWeight = (!higherPriorityMatchFound) ? WEIGHTS.area.immediate : WEIGHTS.area.fulltext;
            best = Math.max(best, fullTextWeight + WEIGHTS.match.exact);
        } else if (includes(ft, query)) {
            // Substring matches never get promoted
            best = Math.max(best, WEIGHTS.area.fulltext + WEIGHTS.match.substring);
        }

        if (best === 0 && ft.length === 0) {
            best = WEIGHTS.emptyText;
        }

        return best;
    };

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
                elements = elements.concat(results.map(x => ({element: x, label: nameInTagContentLabel, label_name: 'nameInTagContent'})));

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
                    elements = elements.concat(results.map(x => ({element: x, label: nameIsAttributeLabel, label_name: 'nameIsAttribute'})));
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
                elements = elements.concat(results.map(x => ({element: x, label: nameInValueLabel, label_name: 'nameInValue'})));
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
                    var labelImmediateText = getImmediateText(label);
                    elements = elements.concat(results.map(x => ({element: x, label: labelForNameLabel, label_name: 'labelForName', immediate_override: labelImmediateText})));
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
                elements = elements.concat(results.map(x => ({element: x, label: nameInNestedChildLabel, label_name: 'nameInNestedChild'})));

                for(var aIndex=0; aIndex < attributes.length; aIndex++) {
                    var attribute_name = attributes[aIndex];
                    var innerNestedElementsLabel = `<${thing}><* ${attribute_name}="${name}"></*></${thing}>`;
                    results = jqCucu(`*:vis[${attribute_name}="${name}"]`, document.body).parents(thing).toArray();
                    if (cucu.debug) { console.log(innerNestedElementsLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: innerNestedElementsLabel, label_name: 'innerNestedElements'})));
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
                    elements = elements.concat(results.map(x => ({element: x, label: nameIsPreviousSiblingLabel, label_name: 'nameIsPreviousSibling'})));
                }
            }

            // element labeled with direct next sibling
            if (direction === RIGHT_TO_LEFT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    var nameIsNextSiblingLabel = `<${thing}/><*>${name}</*>`;
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).prev(thing).toArray();
                    if (cucu.debug) { console.log(nameIsNextSiblingLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: nameIsNextSiblingLabel, label_name: 'nameIsNextSibling'})));
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
                elements = elements.concat(results.map(x => ({element: x, label: nameIsTextSiblingLabel, label_name: 'nameIsTextSibling'})));
            }

            // element labeled with any previous sibling
            if (direction === LEFT_TO_RIGHT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    var leftToRightLabel = `<*>${name}</*>...<${thing}>...`;
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).nextAll(thing + ':vis').toArray();
                    if (cucu.debug) { console.log(leftToRightLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: leftToRightLabel, label_name: 'leftToRight'})));

                    var leftToRightGrandpaLabel = `<...><*>${name}</*></...>...<...><${thing}></...>`;
                    // XXX: this rule is horribly complicated and I'd rather see it gone
                    //      basically: common great grandpranet
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).nextAll().find(thing + ':vis').toArray();
                    if (cucu.debug) { console.log(leftToRightGrandpaLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: leftToRightGrandpaLabel, label_name: 'leftToRightGrandpa'})));
                }
            }

            // element labeled with any next sibling
            if (direction === RIGHT_TO_LEFT) {
                for(var tIndex = 0; tIndex < things.length; tIndex++) {
                    var thing = things[tIndex];

                    var rightToLeftLabel = `<${thing}>...<*>${name}</*>...`;
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).prevAll(thing).toArray();
                    if (cucu.debug) { console.log(rightToLeftLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: rightToLeftLabel, label_name: 'rightToLeft'})));

                    var rightToLeftGrandpaLabel = `<...><${thing}></...>...<...><*>${name}</*></...>`;
                    // XXX: this rule is horribly complicated and I'd rather see it gone
                    results = jqCucu(`*:vis:${matcher}("${name}")`, document.body).prevAll().find(thing + ':vis').toArray();
                    if (cucu.debug) { console.log(rightToLeftGrandpaLabel, results); }
                    elements = elements.concat(results.map(x => ({element: x, label: rightToLeftGrandpaLabel, label_name: 'rightToLeftGrandpa'})));
                }
            }
        }

        // deduplicate elements by element identity, keeping order
        var deduped_elements = [];
        var seen_elements = new Set();
        for (var i = 0; i < elements.length; i++) {
            if (!seen_elements.has(elements[i].element)) {
                seen_elements.add(elements[i].element);
                elements[i].pass = i;
                deduped_elements.push(elements[i]);
            }
        }
        elements = deduped_elements;

        // score and sort by relevance (desc), then earlier pass (asc)
        for (var i2 = 0; i2 < elements.length; i2++) {
            elements[i2].score = cucu.relevance(elements[i2].element, name, elements[i2].immediate_override);
        }
        elements.sort(function(a, b){
            if (b.score !== a.score) return b.score - a.score;
            return a.pass - b.pass;
        });

        // trim low-score elements
        var trimmedElements = [];

        if (elements.length > 0) {
            var highestScore = elements[0].score;
            var threshold, useInclusive;

            // determine threshold and comparison type
            if (highestScore > WEIGHTS.match.substring) {
                threshold = WEIGHTS.match.substring;
                useInclusive = true; // score >= threshold
            } else if (highestScore > 0) {
                threshold = 0;
                useInclusive = false; // score > threshold
            } else {
                // no trimming needed - all elements have score 0 or less
                threshold = null;
            }

            if (threshold !== null) {
                // single pass separation: kept vs trimmed
                var keptElements = [];
                for (var i = 0; i < elements.length; i++) {
                    var element = elements[i];
                    var keep = useInclusive ? (element.score >= threshold) : (element.score > threshold);
                    if (keep) {
                        keptElements.push(element);
                    } else {
                        trimmedElements.push(element);
                    }
                }
                elements = keptElements;
            }
        }

        // scroll to selected index if possible and before logging coords
        if (index < elements.length) {
            elements[index].element.scrollIntoView({block: "center", inline: "center", behavior: "smooth"});

        let debugMsg = `fuzzy_find: found (${elements.length}) matches, returning index ${index}.`;
        for (var i = 0; i < elements.length; i++) {
            const rect = elements[i].element.getBoundingClientRect();
            const content = (elements[i].element.textContent || elements[i].element.innerText || jqCucu(elements[i].element).text() || '').replace(/\n/g, '').trim();
            debugMsg += `\n  [${i}]: score [${elements[i].score}] text '${content}' at (${Math.round(rect.x)}, ${Math.round(rect.y)}) pass [${elements[i].pass}] for ${elements[i].label_name} using ${elements[i].label}`;
        }
        console.debug(debugMsg);

        if (trimmedElements.length > 0) {
            let trimmedDebugMsg = `fuzzy_find: trimmed ${trimmedElements.length} elements below score: ${threshold}`;
            for (var i = 0; i < trimmedElements.length; i++) {
                const rect = trimmedElements[i].element.getBoundingClientRect();
                const content = (trimmedElements[i].element.textContent || trimmedElements[i].element.innerText || jqCucu(trimmedElements[i].element).text() || '').replace(/\n/g, '').trim();
                trimmedDebugMsg += `\n  [${i}]: score [${trimmedElements[i].score}] text '${content}' at (${Math.round(rect.x)}, ${Math.round(rect.y)}) pass [${trimmedElements[i].pass}] for ${trimmedElements[i].label_name} using ${trimmedElements[i].label}`;
            }
            console.debug(trimmedDebugMsg);
        }

        /*
        Explaination of debug output format:
        Here's the breatkdown of the debug output for this single matched element:
        `[0]: text 'blue          green          red' at (93, 8) pass [0] for labelForName using \u003C* for=...>Pick a color\u003C/*>...\u003Cselect id=...>\u003C/select>`

        1. text `blue` is the text content of the found element (includes child text)
        2. at `(93, 8)` the (x, y) coordinates of the top left of the element
        3. pass `[0]` (mostly for internal purposes) is the original index number in which fuzzy found and recorded the element before deduplication
        4. for `labelForName` is the kind of search fuzzy did to find the element
        5. using `\u003C* for=...>Pick a color\u003C/*>...\u003Cselect id=...>\u003C/select>` was the search expression used
        */

        if (elements.length > 0 && insert_label) {
            return [elements[index].element, elements[index].label];
        }
        return elements[index];
    };
})();
