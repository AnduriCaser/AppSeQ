(function (global, $) {
    if (typeof $ === "undefined") {
        errorHandler("This method needs jQuery");
    }

    var plugin = "syn_paginate";


    $.fn[plugin] = function (options) {

        var cont = $(this);

        var attributes = $.extend({}, $.fn[plugin].defaults, options);


        var pagination = {
            init: function () {
                var self = this;

                self.parseUrl(attributes.url, async function (url) {
                    await self.render();
                    await self.setEvent();
                });
            },
            data: async function (page) {
                return new Promise((resolve, reject) => {
                    var pageRange = attributes.pageRange;
                    var perPage = attributes.perPage;

                    params = {
                        type: "GET",
                        url: attributes.url,
                        data: {
                            perPage: attributes.perPage,
                            page: page ? page : 1
                        },
                        contentType: "application/json;charset=UTF-8",
                        dataType: "json",
                    };



                    params.success = function (response) {
                        if (response) {
                            resolve(response);
                        } else {
                            errorHandler("Something went wrong.");
                        };
                    };

                    $.ajax(params);

                });
            },

            render: async function () {
                var self = this;
                var perPage = attributes.perPage || 0;
                var end = attributes.pageRange;
                var data;

                await self.data(null)
                    .then(function (res) {
                        data = res;
                    });


                if (data) {
                    cont.html(self.generatePagesandHTML({
                        data: data,
                        endPage: end
                    }));
                } else {
                    errorHandler("Something went wrong.");
                }
            },

            // Generation pagination html
            generatePagesandHTML: function (args) {
                var self = this;
                var array = [];
                var li;
                var a;
                var totalPage = args.endPage;
                var ul = $('<ul class="pagination"></ul>');
                var li_prev = $('<li class="page-item"></li>');
                var li_next = $('<li class="page-item"></li>');
                var a_prev = $('<a href="#" id="previous" class="page-link"></a>');
                var a_next = $('<a href="#" id="next" class="page-link"></a>');
                var span_prev = $('<span>&laquo;</span>');
                var span_next = $('<span>&raquo;</span>');

                a_prev.append(span_prev);
                a_next.append(span_next);
                li_prev.append(a_prev);
                li_next.append(a_next);

                ul.append(li_prev);
                ul.append(li_next);

                for (let i = 1; i <= totalPage; i++) {
                    li = $('<li class="page-item"></li>');
                    a = $(`<a class="page-link" href="#">${i}</a>`);
                    if (i == 1) {
                        a.css({
                            "background-color": "#943124",
                            "border-radius": "3px",
                            "text-decoration": "none",
                            "color": "white",
                            "pointer-events": "none"
                        });
                    } else {
                        a.css({
                            "border-radius": "3px",
                            "text-decoration": "none",
                            "color": "white",
                        });
                        a.on("mouseover", function () {
                            $(this).css({
                                "border": "1px solid gray",
                                "background-color": "#1d1d1d",
                            });
                        }).on("mouseleave", function () {
                            $(this).css("border", "none");
                        });
                    }

                    li.append(a);
                    array.push(li);
                };

                li_prev.after(array);

                self.getPage(null, null, args.data);

                return ul;
            },

            // Generate CSS Later !!!

            genereatePagesCSS: function (el, target) {
                if (target) {

                } else {

                }
            },

            setEvent: async function () {
                var self = this;
                var element = $("#nav-pagination");


                element.on("click", ".page-link", async function (e) {
                    var target = $(e.target);
                    var page = target.text();
                    var data;

                    $(".page-link").each(function (index, element) {
                        if (!$(element).attr("id")) {
                            if ($(target) !== $(element)) {
                                $(element).css({
                                    "background-color": "#1d1d1d",
                                    "pointer-events": "auto"
                                });
                                $(element).on("mouseover", function () {
                                    $(this).css({
                                        "border": "1px solid gray",
                                        "background-color": "#1d1d1d",
                                    });
                                }).on("mouseleave", function () {
                                    $(this).css("border", "none");
                                });
                            };
                        };
                    });

                    if (!$(target).attr("id")) {
                        $(target).css({
                            "background-color": "#943124",
                            "border-radius": "3px",
                            "text-decoration": "none",
                            "color": "white",
                            "pointer-events": "none"
                        })
                    }

                    if ($.isNumeric(page)) {
                        await self.data(page)
                            .then(function (res) {
                                data = res;
                            });
                        self.getPage(page, target, data);
                    } else {
                        errorHandler("Page number must be number.");
                    }
                });
            },

            getPage: function (page, target, data) {
                var self = this;
                var el = $("#paginate");
                var items = $(".page-item");
                var html;
                if (page) {
                    if (target) items.each(function (index, element) { $(element).removeClass("active"); }); target.parent().addClass("active");
                }
                data.forEach(element => {
                    html += `<tr class="border-0">
                                <td>
                                    <label
                                        class="form-check form-check-inline form-check-solid">
                                        <input
                                            style="background-color: #444;border-radius: 3px;cursor: pointer;"
                                            class="form-check-input border-0" type="checkbox">
                                    </label>
                                </td>
                                <td>
                                    <div class="d-flex align-items-center">
                                        <div class="d-flex justify-content-start flex-column">
                                            <span style="color: rgb(185, 185, 185);"
                                                class="fw-bolder fs-6">${element.name}</span>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span style="color: rgb(185, 185, 185);"
                                        class="fw-bolder fs-6">${element.description}</span>
                                </td>
                                <td>
                                    <span style="color: rgb(185, 185, 185);"
                                        class="fw-bolder d-block  fs-6 text-center">${element.points}</span>
                                </td>
                                <td>
                                    <span style="color: rgb(185, 185, 185);"
                                        class="fw-bolder d-block  fs-6 text-center">${element.difficulty}</span>
                                </td>
                        </tr>`;
                });

                el.html(html);
            },

            previousPage: function () {

            },

            nextPage: function () {

            },

            parseUrl: function (url, callback) {
                if (typeof url === 'string') {
                    if (url === '/admin/api/labs') {
                        // attributes.ajaxDataType = 'jsonp';
                        callback(url);
                    };
                } else {
                    errorHandler("Invalid Url");
                }
            }
        };

        checkParams(attributes);

        pagination.init();
    }

    $.fn[plugin].defaults = {
        url: '',
        pageRange: 2,
        perPage: 1,
        cssFramework: "Bootstrap 5",
        showPrev: true,
        showNext: true,
    }

    function errorHandler(content) {
        throw new Error("PaginationError :" + content);
    };


    function checkParams(args) {
        if (args.url === 'undefined') {
            errorHandler("Url is empty");
        }
        if (args.ajax === 'undefined') {
            errorHandler('Ajax is empty.');
        }
        if (typeof args.url === 'string') {
            if (!$.isNumeric(args.perPage)) {
                errorHandler("(dataPerPage) must be a number.");
            } else if (!$.isNumeric(args.pageRange)) {
                errorHandler("(pageRange) must be a number.");
            }
        }
        else {
            errorHandler("Url must be string.");
        }
        // if (typeof args.ajax === 'object') {
        //     if (args.ajax.beforeSend === 'undefined') {
        //         errorHandler("Before send mustn't be empty !");
        //     }
        // } else {
        //     errorHandler("Ajax must be object.");
        // }
    }

}(this, window.jQuery))