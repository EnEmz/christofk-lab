function ColorManager(){
    
    this.theme = "default"
    
    this.themes = {};
    
    this.themes["default"] = ["red", "green", "blue", "yellow", "orange", "teal"];
    this.active_colors = this.themes["default"];
    
    this.index = 0;
    
    this.setTheme = function (theme){
        
        this.theme = theme;
        this.active_colors = this.themes[this.theme];
        this.index = -1;
    }
    
    
    this.nextColor = function(){
        
        this.index = (this.index + 1)%this.active_colors.length;
        return this.active_colors[this.index];
    }
}



function ChromatogramView(){
    
   this.chromatogram = null;

   this.node = $("<div>");
   this.node.addClass("chromatogram");
    
   this.canvas = $("<canvas>");
   this.node.append(this.canvas);
    
   this.dimensions = {width:500, height:100};

   this.stroke_params = {width:2, color:"black"};
   this.points_params = {r:0, color:"black"};
   this.shade_color = null;
}


ChromatogramView.prototype.addOverlayText = function(text, x, y){
    
    
    var text_box = $("<div class = 'overlay_text'>" + text +"</div>")
    
    text_box.css("left", x);
    text_box.css("top", y);
    
    this.node.append(text_box);
}

ChromatogramView.prototype.setOverlayTextVisible = function(visible){
    
    var display = "none";
    
    if(visible) display = "block";
    
    this.node.find(".overlay_text").css("display", display)
}

ChromatogramView.prototype.setStrokeWidth = function(w){
    
   this.stroke_params.width = w;
     this.update();
}

ChromatogramView.prototype.setStrokeColor = function(color){
    
   this.stroke_params.color = color;
   this.update();
}

ChromatogramView.prototype.setPointRadius = function (r){
    
    this.points_params.r = r;
    this.update();
}


ChromatogramView.prototype.setPointColor = function (color){
    
    this.points_params.color = color;
    this.update();
}

ChromatogramView.prototype.setShadeColor = function(color){
    
    this.shade_color = color;
   this.update();
}

ChromatogramView.prototype.setGlobalOffset = function(x, y){
    
    this.node.css("left", "calc(50% + " + x + "px)");
    this.node.css("top", y + "px");
}


ChromatogramView.prototype.addToNode = function(parent_node){
    
    parent_node.append(this.node);
}

ChromatogramView.prototype.setDimensions = function (w, h){
    
    this.dimensions = {width:w, height:h};
    
    this.update();
}

ChromatogramView.prototype.setDomain = function (min, max){
    
    this.domain = {min:min, max:max};
    
    this.update();
}

ChromatogramView.prototype.setDisplayDomain = function(min, max){
    
    if(max < min) return ;
    
    this.display_domain = {min:min, max:max};
    this.update();
}


ChromatogramView.prototype.setRange = function (min, max){
    
    this.range = {min:min, max:max};
    this.update();
}

ChromatogramView.prototype.setChromatogram = function(chrom){
    
    this.chromatogram = chrom;
    
    if(chrom != null){
        
        var span = chrom.span();
        
        this.domain = {min:span.start, max:span.end};
        this.range = {min:0, max:1.05*chrom.mostIntensePointInSpan(span)[2]};
    }
    
    this.update();
}

ChromatogramView.prototype.viewCoordsFromDataPoint = function(dataPoint){
    
    var w = this.dimensions.width, h = this.dimensions.height;
    
    var x = (dataPoint[0]-this.domain.min)*w/(this.domain.max-this.domain.min);
    var y = h - (dataPoint[2]-this.range.min)*h/(this.range.max-this.range.min);
    return {x:x, y:y};
}





ChromatogramView.prototype.update = function(){
    
    this.canvas.attr("width", this.dimensions.width);
    this.canvas.attr("height", this.dimensions.height);
    
    
    if(this.chromatogram == null || this.chromatogram.points.length < 1) return;

    
    
    var ctx = this.canvas[0].getContext("2d");
    ctx.lineWidth = this.stroke_params.width;
    ctx.strokeStyle = this.stroke_params.color;
    
    
    var pts =  this.chromatogram.points;
    
    
     if(this.display_domain == null){
        
        this.display_domain = {min:pts[0][0], max: pts[pts.length - 1][0]};
    }
    
    
    
    ctx.beginPath();
    
    var visible = false;
    
    var first_point_x = 0;
    
    for(var i = 0, n = pts.length; i < n; i++){
        
        
        var point = pts[i];
        var coords = this.viewCoordsFromDataPoint(point);
        
        if(visible == false && point[0] >= this.display_domain.min){
            
            visible = true;
            first_point_x = coords.x
            ctx.moveTo(coords.x, coords.y);
        }
        
        if(visible == false) continue;
        
        if(point[0] > this.display_domain.max) break;
        
        ctx.lineTo(coords.x, coords.y);
    }
    
    if(this.stroke_params.color != null) ctx.stroke();
    
    if(this.shade_color != null){
        
         ctx.fillStyle = this.shade_color;

         ctx.lineTo(coords.x, this.dimensions.height);
         ctx.lineTo(first_point_x, this.dimensions.height);
         ctx.closePath();
        
         ctx.fill();
    }
    
    if(this.points_params.r > 0){
     
         ctx.beginPath();
    
        var r = this.points_params.r;
    
        for(i = 0, n = pts.length; i < n; i++){
        
            coords = this.viewCoordsFromDataPoint(pts[i]);
            ctx.arc(coords.x, coords.y,r, 0, 2*Math.PI);
         }
        
        ctx.fillStyle = this.points_params.color;
        ctx.fill();
    }    
}




function MZXMLIcon(filename){
    
    this.node = null;
    this.name = filename;
    
    this.node = $( '<div class = "mzml_file_icon">'+this.name +'<div>');
    this.node.append($('<div class="progress_bar"></div>'));
    this.progress_bar = this.node.find(".progress_bar");
    
    this.node.on("click", function(){
        
        $(this).toggleClass("active");
    })
}

MZXMLIcon.prototype.addToNode = function (node){
        
        node.append(this.node);
    }

MZXMLIcon.prototype.setProgress = function(progress){
        
        var per = Math.ceil(progress*100) +"%";
        this.progress_bar.css("width", per);
}



function SampleIcon(name){
    
    this.node = null;
    this.name = filename;
    
}



function Sample(name){
    
    this.name = name;
    this.group_index = 0;
    this.data = {};
    this.id = "SID-" + Math.floor(10000000*Math.random());
    
    this.style = {
        
        stroke:true,
        fill:true,
        stroke_color:"black",
        stroke_width:1,
        fill_color:"red",
        x_offset:0,
        y_offset:0,
        show_text:false
    }
    
    
    this.setPosFile = function(p_file){
        
        this.data["pos"] = p_file;
    }
    
    this.setNegFile = function(n_file){
        
          this.data["neg"] = n_file;
    }
    
    this.setGroupIndex = function(index){
        
        this.group_index = index;
    }
    
    this.getDisplayName = function(){
        
        return this.name;
    }
    
    this.getChromatogram = function(polarity, mz_range){
        
        if(polarity == "neg" && this.data["neg"] != undefined){
            
            return this.data["neg"].extractChromatogram(mz_range);
        }
        else if(polarity == "pos" && this.data["pos"] != undefined){
            
            return this.data["pos"].extractChromatogram(mz_range);
        }
        
        return null;
    }
    
    this.setStyle = function(style){
        
        this.style = style;
        this.updateChromatogramView();
    }
    
    this.updateChromatogramView = function(){
        
        if(this.cv == undefined || this.cv== null) return;
        
        if(this.style.stroke) this.cv.setStrokeColor(this.style.stroke_color);
        else this.cv.setStrokeColor(null);
        
        this.cv.setStrokeWidth(this.style.stroke_width);
        
        if(this.style.fill) this.cv.setShadeColor(this.style.fill_color);
        else this.cv.setShadeColor(null);
        
        this.cv.setGlobalOffset(this.style.x_offset, this.style.y_offset);
        
        this.cv.setOverlayTextVisible(this.style.show_text);
    }
}


function SampleGroup(name){
    
    this.name = name;
    this.samples = [];
    
    this.addSample = function (sample){
        
        sample.setGroupIndex(this.samples.length + 1);
        this.samples.push(sample);
    }
    
    this.getSamples = function(){
        
        return this.samples;
    }
    
    this.getNumSamples = function(){
        
        return this.samples.length;
    }
    
     this.getDisplayName = function(){
        
        return this.name;
    }
}




function SampleMenu(){
    
    
    this.node = $("<div class = 'group_list'></div>")
    
    this.groups = [];
    
    
    this.addToNode = function(parent){
        
        parent.append(this.node);
    }
    
    this.addNewGroup = function(group){
        
        var group_node = $('<div class = "group open"></div>');
        
        group_node.append($('<div class = "g_title inspectable"><input class = "g_chck" type ="checkbox">' + group.getDisplayName() + '<div class = "toggle_sh"></div>'))
        
        var s_list = $('<div class = "s_list"></div>');
        group_node.append(s_list);
        
        var sample_ids = [];
        
        for(var s of group.getSamples()){
            
            var sample_id = s.id;
            sample_ids.push(s.id);
            
            var sample_node = $('<div class = "s"></div>');
            sample_node.append($('<div class = "s_title inspectable" data-sid="' + sample_id + '"><input class = "s_chck" type ="checkbox">'+ s.getDisplayName() +'<div class = "toggle_sh"></div></div>'));
            
            var file_list = $('<div class = "f_list"></div>');
            sample_node.append(file_list);
            
            if(s.data["neg"] != undefined)  file_list.append($(' <div class = "f_title">neg</div>'));
            if(s.data["pos"] != undefined)  file_list.append($(' <div class = "f_title">pos</div>'));
            
            s_list.append(sample_node);
        }
        
        
        var pooled_ids = sample_ids.join(":");
        group_node.find(".g_title").attr("data-sid", pooled_ids);
        
        
        group_node.find(".g_chck").on("input", function(){
            
            var checked = $(this).is(":checked");    
            $(this).parents().eq(1).find('.s_chck').prop('checked', checked)
        })
        
         group_node.find(".s_chck").on("input", function(){
             
             var all_checked = true;
             
            $(this).parents().eq(2).find(".s_chck").each(function(i, e){
                
                if($(this).is(":checked") == false) all_checked = false;
            })
             
            $(this).parents().eq(3).find('.g_chck').prop('checked', all_checked);
        })
        
        
        group_node.find(".toggle_sh").on("click", function(){
            
            $(this).parents().eq(1).toggleClass("open");
        })
        
        group_node.find('.inspectable').hover(function(e){
            
            var x = $(this).offset().left + $(this)[0].getBoundingClientRect().width +0.5;
            var y =  $(this).offset().top;
            
            
            var id_str = $(this).attr("data-sid");
            
            var sample = SAMPLES_FROM_ID_STRING(id_str)[0];
            
            var inspector = $("#floating_inspector");
            
            $("#stroke_toggle").prop( "checked", sample.style.stroke);
            $("#fill_toggle").prop("checked", sample.style.fill);
            $("#stroke_color").spectrum("set", sample.style.stroke_color);
            $("#stroke_width").val(sample.style.stroke_width);
            $("#fill_color").spectrum("set", sample.style.fill_color);
            $("#sample_x_offset").val(sample.style.x_offset);
            $("#sample_y_offset").val(sample.style.y_offset);
            $("#show_name_toggle").prop("checked", sample.style.show_text);
            inspector.attr("linked-sample-ids", id_str);
            inspector.css("left",x + "px");
            inspector.css("top",y + "px");
            
            $(this).append(inspector);
            
        }, function(e){

            $("#floating_inspector").css("top","-1000px");
            
        })
        
        this.node.append(group_node);
    }
    
}
