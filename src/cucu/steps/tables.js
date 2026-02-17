(function(){
    window.findAllTables = function() {
        var tables = [];

        function tableToJSON(table) {
            var data = [];
            var rowSpanMap = [];

            for (var rIndex = 0; rIndex < table.rows.length; rIndex++) {
                var row = table.rows[rIndex];
                var values = [];
                var vIndex = 0;

                // Fill values from active rowspans
                while (rowSpanMap[vIndex]) {
                    values.push(rowSpanMap[vIndex].value);
                    rowSpanMap[vIndex].span--;
                    if (rowSpanMap[vIndex].span === 0) {
                        delete rowSpanMap[vIndex];
                    }
                    vIndex++;
                }

                for (var cIndex = 0; cIndex < row.cells.length; cIndex++) {
                    var value = row.cells[cIndex].innerText.trim();
                    value = value.replace(/[\r\n\s]+/g, " ");

                    var rowspan = row.cells[cIndex].rowSpan || 1;
                    var colspan = row.cells[cIndex].colSpan || 1;

                    for (var i = 0; i < colspan; i++) {
                        values.push(value);

                        if (rowspan > 1) {
                            rowSpanMap[vIndex] = {
                                value: value,
                                span: rowspan - 1
                            };
                        }
                        vIndex++;
                    }
                }

                if (values.length !== 0) {
                    data.push(values);
                }
            }
            return data;
        }

        var table_elements = document.querySelectorAll('table');
        for (var index = 0; index < table_elements.length; index++) {
            tables.push(tableToJSON(table_elements[index]));
        }

        return tables;
    };
})();
