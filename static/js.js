


function isEmail(email){
        //对电子邮件的验证
     var myreg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
     if(!myreg.test(email)){
                 return false;
        }
        else
            return true;
    }

    function isPwd(password)
    {
        var myreg = /[0-9a-zA-Z]+/;
        if(!myreg.test(password))
            return false;
        else
            return true;

    }
    function inputpassword()
    {
        var password=$("#pwd").val();
        var tip2=$("#tip2");
        var tip_2=$("#tip_2");
        if(password.length<8)
        {
            $("#pwd").next().css("display","none");
            tip2.css("display","block");
            tip_2.html("请输入8位以上密码！");
        }
        else if(!isPwd(password)){
            $("#pwd").next().css("display","none");
            tip2.css("display","block");
            tip_2.html("密码仅由英文或数字组成！");
        }
        else{
            tip2.css("display","none");
            $("#pwd").next().css("display","block");
        }
    }
    var inputs=document.getElementsByTagName("input");
    for(var i=0;i<inputs.length;i++)
    {
        inputs[i].onkeyup=function(event){
            if(event.keyCode=13){
                var next=this.nextElementSibling.nextElementSibling;
                next.focus();
            }
        }
    }