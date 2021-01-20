//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    // 查询房客订单
    $.ajax({
        url: host + "/api/v1.0/orders?role=custom",
        type: "get",
        xhrFields: {withCredentials: true},
        success: function (resp) {
            if ("0" == resp.errno) {
                $(".orders-list").html(template("orders-list-tmpl", {orders: resp.data.orders}));
                $(".order-comment").on("click", function () {
                    var orderId = $(this).parents("li").attr("order-id");
                    $(".modal-comment").attr("order-id", orderId);
                });
                $(".modal-comment").on("click", function () {
                    var orderId = $(this).attr("order-id");
                    var comment = $("#comment").val()
                    if (!comment) return;
                    var data = {
                        comment: comment
                    };
                    // 处理评论
                    $.ajax({
                        url: host + "/api/v1.0/orders/" + orderId + "/comment",
                        type: "PUT",
                        data: JSON.stringify(data),
                        contentType: "application/json",
                        dataType: "json",
                        headers: {
                            "X-CSRFToken": getCookie("csrf_token"),
                        },
                        xhrFields: {withCredentials: true},
                        success: function (resp) {
                            if ("4101" == resp.errno) {
                                location.href = "/login.html";
                            } else if ("0" == resp.errno) {
                                $(".orders-list>li[order-id=" + orderId + "]>div.order-content>div.order-text>ul li:eq(4)>span").html("已完成");
                                $("ul.orders-list>li[order-id=" + orderId + "]>div.order-title>div.order-operate").hide();
                                $("#comment-modal").modal("hide");
                            }
                        }
                    });
                });

            $(".order-accept").on("click", function () {
                // 获取订单id
                var orderId = $(this).parents("li").attr("order-id");
                // 设置到弹框的确认键上,以及后续获取
                $(".modal-accept").attr("order-id", orderId);
                $(".modal-accept").attr("amount", resp.data.orders.amount);

            });
            // TODO:支付处理
            // $(".modal-accept").on("click", function () {
            //     // 获取订单id
            //     var orderId = $(this).attr("order-id");
            //     var amount = $(this).attr("amount");
            //     $.ajax({
            //         url: host + "/api/v1.0/orders/" + orderId + "/pay",
            //         type: "PUT",
            //         data: JSON.stringify({"action":"accept","amount":amount}),
            //         contentType: "application/json",
            //         dataType: "json",
            //         xhrFields: {withCredentials: true},
            //         headers: {
            //             "X-CSRFTOKEN": getCookie("csrf_token"),
            //         },
            //         success: function (resp) {
            //             if ("4101" == resp.errno) {
            //                 location.href = "/login.html";
            //             } else if ("0" == resp.errno) {
            //                 // 1. 设置订单状态的html
            //                 $(".orders-list>li[order-id=" + orderId + "]>div.order-content>div.order-text>ul li:eq(4)>span").html("已支付");
            //                 // 2. 隐藏接单和拒单操作
            //                 $("ul.orders-list>li[order-id=" + orderId + "]>div.order-title>div.order-operate").hide();
            //                 // 3. 隐藏弹出的框
            //                 $("#accept-modal").modal("hide");
            //             }
            //         }
            //     })
            // });
        }
        }
    })
});
