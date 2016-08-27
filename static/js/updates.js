$(function() {

    function update(){

        $.getJSON('/updates', {}, function(data) {
            
            if(data != 0){
                $('#chatbox').append("<p>" + data[0][0] + ":" + data[0][1] + ": " + data[1] + "</p>")
                
            }

        });
        
    }

    setInterval(update, 1000);


});