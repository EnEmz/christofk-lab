function sum(values){
    
    var s = 0;
    
    for(var i = 0, n = values.length; i < n;i++){
        
        s += values[i];
    }
    
    return s;
}

function mean(values){
    
    return sum(values)/values.length;
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function numberValues(values){
    
    var num_values = [];
    
    for(var i = 0, n = values.length; i < n; i++){
            
        if(isNumber(values[i]) === true){
            
            num_values.push(parseFloat(parseFloat(values[i]).toFixed(3)));
        }
    }
    
    return num_values;   
}

function series(start, length, increment){
    
    if(increment === undefined) increment = 1;
    
    var integers = [];
    var value = start;
    
    for(var i = 0; i < length; i ++){
        
        integers.push(value);
        value += increment;
    }
    
    return integers;
}

function max(values){
    
    if(values.length === 0) return null;
    
    var current_max = values[0];
    
    for(var i = 0, n = values.length; i < n; i++){
            
        if(values[i] > current_max){
            
            current_max = values[i];
        }
    }
    
    return current_max;
}

function min(values){
    
    if(values.length === 0) return null;
    
    var current_min = values[0];
    
    for(var i = 0, n = values.length; i < n; i++){
            
        if(values[i] < current_min){
            
            current_min = values[i];
        }
    }
    
    return current_min;
}

function reverse(values){
    
    var reversed = [];
    for(var i = values.length - 1; i >= 0; i++){
            
        reversed.push(values[i]);
    }   
    
    return reversed;
}

function separate(values, string){
    
    var separated_values = [];
    var current_array = [];
    
    for(var i = 0, n = values.length; i < n; i++){
            
        if(values[i] === string){
            
            if(current_array.length > 0){
                
                separated_values.push(current_array);
                current_array = [];
            }
            
            continue;
        }else{
            
            current_array.push(values[i]);
        }
    }
    
    if(current_array.length > 0){
                
        separated_values.push(current_array);
    }
    
    return separated_values;
}

function collapse(values){
    
    var new_values = [];
    
    for(var i = 0, n = values.length; i < n; i++){
            
        if(values[i].toString().trim() !== ''){
            
            new_values.push(values[i]);
        }
    }
    
    return new_values; 
}

function between(string, left, right){
    
    return string.substring(string.indexOf(left) + left.length, string.indexOf(right));
}

function CSVTable(){
    
    this.values = [];
    
    var _this = this;
    
    //**************************************************SETUP CODE*****************************************************
    
    if(arguments.length === 1 && typeof arguments[0] === "string"){

            var lines = arguments[0].split(String.fromCharCode(13));
            var length = lines.length;
            while(length > 1 && (lines[length - 1]).toString().trim() === ""){

                lines.pop();
                length--;
            }

            for(var r = 0, nr = lines.length; r < nr; r++){

                this.values[r] = lines[r].split(",");
                this.trimEmptyRowEnd(r);
            }
    }
    else{
        
        for(var i = 0, n = arguments.length; i < n; i++){
        
            var argument = arguments[i];
            
            if(typeof argument === "object"){

                if(argument.hasOwnProperty("column")){

                    this.addColumnData(argument.column);
                }
                else if(argument.hasOwnProperty("columns")){

                    var columns = argument.columns;
                    for(var i = 0, n = columns.length; i < n; i++){
                        
                        this.addColumnData(columns[i]);
                    }
                }
                else if (argument.hasOwnProperty("row")){

                    this.addRowData(argument.row);
                }
                else if(argument.hasOwnProperty("rows")){

                    var rows = argument.rows;
                    for(var i = 0, n = rows.length; i < n; i++){
                        
                        this.addRowData(rows[i]);
                    }
                }
            }
        }
    }
}

CSVTable.prototype.numberOfColumns = function (){

    var max_columns = -1;

    for(var r = 0, nr = this.values.length; r < nr; r++){

        if(this.values[r].length > max_columns) max_columns = this.values[r].length;
    }

    return max_columns;
}

CSVTable.prototype.numberOfRows = function (){

    return this.values.length;
}

CSVTable.prototype.hasRow = function(row_num){

    var r = row_num - 1;
    return (r > -1 && r < this.values.length);
}

CSVTable.prototype.valueAt = function (csv_position){

    var r = csv_position.row - 1, c = csv_position.column - 1;

    if(r > -1 && r < this.values.length){

        if(c > -1 && c < this.values[r].length){

            return this.values[r][c];
        }
    }

    return null;
}

CSVTable.prototype.setValueAt = function (csv_position, value){
    
    if(typeof csv_position === "object" && csv_position.hasOwnProperty("row") && csv_position.hasOwnProperty("column")){

        var r = csv_position.row - 1, c = csv_position.column - 1;

        if(this.hasRow(csv_position.row)){

            if(c > -1 && c < this.values[r].length){

                this.values[r][c] = value;
                if(value.toString().trim() === ""){

                    this.trimEmptyRowEnd(r);
                }
                return true;
            }
        }
        
    }

    return false;
}

CSVTable.prototype.positionsWithValue = function (string, max_num_matches){

    var positions = [];

    var max_number_matches_defined = !(max_num_matches === undefined);
    
    if(max_number_matches_defined){
        
        for(var r = 0, nr = this.values.length; r < nr; r++){

            for(var c = 0, nc = this.values[r].length; c < nc; c++){

                if(this.values[r][c] == string){

                    positions.push({"row":r + 1, "column": c + 1});

                    if(positions.length === max_num_matches) return positions;
                }
            }
        }
        
    }
    else{   
        
        for(var r = 0, nr = this.values.length; r < nr; r++){

            for(var c = 0, nc = this.values[r].length; c < nc; c++){

                if(this.values[r][c] == string){

                    positions.push({"row":r + 1, "column": c + 1});
                }
            }
        }
    }

    return positions;
}

CSVTable.prototype.valuesInColumn = function (column_num, collapsed){
    
    if(collapsed === undefined) collapsed = false;
    
    var c = column_num - 1;

    var column_values = [];
    for(var r = 0, nr = this.values.length; r < nr; r++){

       if(c > -1 && c < this.values[r].length){

           column_values.push(this.values[r][c]);
       }else{
           column_values.push("");
       }
    }

    if(collapsed){

        for(var i = column_values.length - 1; i >= 0; i--){

            if(column_values[i].toString().trim() === ""){

                column_values.splice(i, 1);
            }
        }
    }
    else{

        var length = column_values.length;

        while(length > 0 && (column_values[length - 1]).toString().trim() === ""){

            column_values.pop();
            length--;
        }
    }

   return column_values;
}

CSVTable.prototype.numberValuesInColumn = function (column_num){
    
    return numberValues(this.valuesInColumn(column_num)); 
}

CSVTable.prototype.valuesInRow = function (row_num){

    if(this.hasRow(row_num)){

        return this.values[row_num - 1];
    }

    return null;
}

CSVTable.prototype.numberValuesInRow = function (row_num){
    
    return numberValues(this.valuesInRow(row_num)); 
}

CSVTable.prototype.replace = function (from_string, to_string){

    for(var r = 0, nr = this.values.length; r < nr; r++){

        for(var c = 0, nc = this.values[r].length; c < nc; c++){

            if(this.values[r][c] == from_string){

                this.values[r][c] = to_string;
            }
        }
    }

    if(to_string.toString().trim() === "") this.trimAllEmptyRowEnds();
    
    return this;
}

CSVTable.prototype.removeRows = function (row_start, num_rows){

    if(num_rows === undefined) num_rows = 1;

    if(this.hasRow(row_start)){

        this.values.splice(row_start - 1, num_rows);
    }

    return this;
}

CSVTable.prototype.removeColumns = function (column_start, num_columns){

    var c = column_start - 1;

    if(num_columns === undefined ) num_columns = 1;

    for(var r = 0, nr = this.values.length; r < nr; r++){

       if(c > -1 && c < this.values[r].length){

           this.values[r].splice(c, num_columns);
       }
    }

    this.trimEmptyRowEnds();
    
    return this;
}

CSVTable.prototype.horizontallyAppendFile = function(file, column_gap){

    if(this === file) file = file.copy();

    if(column_gap === undefined) column_gap = 0;

    var num_columns = this.numberOfColumns() + column_gap;

    var left_num_rows = this.numberOfRows(), right_num_rows = file.numberOfRows();

    var num_rows_to_combine = left_num_rows;
    var left_file_shorter = true;

    if(right_num_rows < num_rows_to_combine){

        num_rows_to_combine = right_num_rows;
        left_file_shorter = false;
    }

    for(var r = 0, nr = num_rows_to_combine; r < nr; r++){

       var row = this.values[r];

       var difference = num_columns - row.length;

       if(difference > 0){

           for(var i = 0; i < difference; i++){

               row.push("");
           }
       }

       this.values[r] = row.concat(file.values[r]);
    }

    if(left_file_shorter){

        var rows_to_add = right_num_rows - left_num_rows;

        for(var r = num_rows_to_combine, nr = num_rows_to_combine + rows_to_add; r < nr; r++){

            var row = []

            for(var i = 0; i < num_columns; i++){

                row.push("");
            }

            this.values[r] = row.concat(file.values[r]);
        }
    }

    this.trimAllEmptyRowEnds();
    
    return this;
}

CSVTable.prototype.verticallyAppendFile = function(file, row_gap){

    if(row_gap === undefined) row_gap = 0;

    for(var i = 0; i < row_gap; i++){

        this.values.push([""]);
    }

    this.values = this.values.concat(file.values);
    
    return this;
}

CSVTable.prototype.addRowData = function(data){

    if(data.constructor === Array){

        this.values.push(data.slice());
        var all_data_removed = this.trimEmptyRowEnd(this.values.length - 1);
        if(all_data_removed){

            this.values.pop();
        }

        return this;
    }

    return this;
}

CSVTable.prototype.addColumnData = function(data){

    if(data.constructor === Array){

        var data_num_rows = data.length;

        while(data_num_rows > 0 && (data[data_num_rows - 1]).toString().trim() === ""){

            data.pop();
            data_num_rows--;
        }

        if(data_num_rows === 0) return false;

        var num_rows = this.values.length;
        var data_has_more_rows = true;
        var rn = num_rows;

        if(data_num_rows < num_rows){

            rn = data_num_rows
            data_has_more_rows = false;
        }

        var num_columns = this.numberOfColumns();

        for(var r = 0; r < rn; r++){

            var row = this.values[r];
            var difference = num_columns - row.length;
            if(difference > 0){

                for(var i = 0; i < difference; i++){

                    row.push("");
                }
            }

            this.values[r].push(data[r]);
        }

        if(data_has_more_rows){

            var num_rows_to_add = data_num_rows - num_rows;

            for(var r = rn, n = rn + num_rows_to_add; r < n; r++){

                this.values[r] = [];
                var row = this.values[r];

                for(var i = 0; i < num_columns; i++){

                    row.push("");
                }

                row.push(data[r]);
            }
        }

        this.trimAllEmptyRowEnds();
    }

    return this;
}

CSVTable.prototype.addDataToColumn = function(column_num, data){

    if(data.constructor === Array){

        var data_num_rows = data.length;

        while(data_num_rows > 0 && (data[data_num_rows - 1]).toString().trim() === ""){

            data.pop();
            data_num_rows--;
        }

        if(data_num_rows === 0) return false;
        
        
        var num_rows = this.values.length;
        var bottom_row = -1;
        
        for(var r = num_rows - 1; r >= 0; r--){
            
            var row = this.values[r];
            
            if(row.length >= column_num){
                
                if(row[column_num - 1].toString().trim() !== ""){
                    
                    bottom_row = r;
                    break;
                }
            }
        }
        
        var data_index = 0;
        
        if(bottom_row < num_rows - 1){
            
            for(var r = bottom_row + 1; r < num_rows; r++){
                
                var row = this.values[r];
                
                var difference = column_num - row.length;
                if(difference > 0){

                    for(var i = 0; i < difference - 1; i++){

                        row.push("");
                    }
                    
                    if(data_index < data_num_rows){
                        
                        row.push(data[data_index]);
                        data_index++;
                        
                    }else{
                        
                        return this;
                    }
                    
                }else{
                    
                    if(data_index < data_num_rows){
                        
                        row[column_num - 1] = data[data_index];
                        data_index++;
                        
                    }else{
                        
                        return this;
                    }
                }
                
            }
            
        }

        var num_rows_to_add = data.length - data_index;
        var num_columns = column_num - 1;

        for(var r = num_rows, n = num_rows + num_rows_to_add; r < n; r++){

            this.values[r] = [];
            var row = this.values[r];

            for(var i = 0; i < num_columns; i++){

                row.push("");
            }

            row.push(data[data_index]);
            data_index++;
        }

        this.trimAllEmptyRowEnds();
    }

    return this;
}

CSVTable.prototype.add = function (action_string, data){
    
    action_string = action_string.trim();
    
    var first_letter = action_string.charAt(0);
    var number = -1;
    
    if(action_string.length > 1){
        
        number = parseInt(action_string.substring(1));
    }
    
    if(first_letter.toLowerCase() === 'c'){
        
        if(number > 0){
            
            this.addDataToColumn(number, data);
        }
        else{
            
            this.addColumnData(data);
        }
        
    }else{
        
        if(number > 0){
            
        }
        else{
            
            this.addRowData(data);
        }
    }
    
    return this;
}

CSVTable.prototype.copy = function (){

    var new_file = new CSVTable();

    for(var r = 0, nr = this.values.length; r < nr; r++){

        new_file.values.push([]);
        var row = this.values[r];
        var file_row = new_file.values[r];

        for(var c = 0, nc = row.length; c < nc; c++){

            file_row[c] = row[c];
        }
    }

    return new_file;
}

CSVTable.prototype.trimEmptyRowEnd = function(row_num, all_the_way){

    var row = this.values[row_num];
    var length = row.length;

    var limit = 1;

    if(all_the_way === true){

        limit = 0;
    }

    while(length > 0 && row[length - 1].toString().trim() === ""){

        row.pop();
        length--;
    }

    if(length === 0) return true;
    return false;
}

CSVTable.prototype.trimAllEmptyRowEnds = function (){

    for(var r = 0, nr = this.values.length; r < nr; r++){

        this.trimEmptyRowEnd(r);
    }
}

CSVTable.prototype.toString = function (){

    var string_comps = [];

     for(var r = 0, nr = this.values.length; r < nr; r++){

        string_comps.push(this.values[r].join(","));
    }

    return string_comps.join("\r\n");
}

CSVTable.prototype.downloadAs = function(filename) {
 
    var link = document.createElement('a');
    link.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(this.toString()));
    link.setAttribute('download', filename);
    link.style.display = 'none';

    document.body.appendChild(link);
    
    link.click();
    
    document.body.removeChild(link);
}

