!function($){

    "use strict";

    var RIGHT_COLUMN = 'right_column';
    var LEFT_COLUMN = 'left_column';
    var CENTER_COLUMN = 'center_column';

    var SMALL_WIDTH = 240;
    var MEDIUM_WIDTH = 493;
    var LARGE_WIDTH = 746;
    var ESCAPE_MARGIN = 13;
    var STEP = 240 + ESCAPE_MARGIN;

    $.fn.move_columns = function(columns, line, type) {
        var best = {
            left_column: null,
            center_column: null,
            right_column: null
        }
        for (var key in columns) {
            if (columns[key] == null) {continue;}
            columns[key].find('div.overlay').each(function() {
                var this_line = ($(this).offset().top + $(this).height()) / 2
                if (this_line > line) {
                    if (best[key] == null || (best[key].offset().top + best[key].height()) / 2 > this_line) {
                        best[key] = $(this);
                    }
                }
            });
        }
        if (type == 'up') {
            for (var key in best) {
                if (best[key] == null) {
                    for (var alt_key in columns) {
                        if (alt_key == key && columns[key] != null) {best[key] = columns[alt_key].find('div.overlay').last()}
                    }
                    continue;
                }
                best[key] = best[key].prev().length > 0 ? best[key].prev() : null;
            }
        }
        return best;
    }

    $.fn.reduce_picture = function(image, old_width, old_height, best_down, best_up) {
        var _this = this
        var image_container = image.find('.vignette');

        image.css('cursor', 'pointer');
        image.unbind('click').bind('click', function(event) {
            event.preventDefault()

            $('html, body').animate({scrollTop: $(this).offset().top - 200}, 500);
            image_container.animate({
                width: old_width,
                height: old_height,
                zIndex: -1,
                marginLeft: 0
            },
            {
                duration: 500,
                complete: function() {
                    image.find('.delete-photo').show();
                    image.find('.vignette-description').show()
                    image.addClass('js-overlay');
                    image.css('overflow', 'hidden');
                    for (var key in best_down) {
                    var elt = best_down[key]
                    if (elt == null){continue;}
                        elt.animate({
                            marginTop: 0
                        },500);
                    }
                    for (var key in best_up) {
                        var elt = best_up[key]
                        if (elt == null){continue;}
                        elt.parents('.column').children().first().animate({
                            marginTop: 0
                        }, 500);
                    }
                    $('#gallery div.overlay.expandable').css('cursor', 'pointer')
                    $('#gallery div.overlay.expandable').unbind('click').bind('click', function(event) {
                        event.preventDefault()

                        $('#gallery div.overlay').css('cursor', 'default')
                        $('#gallery div.overlay').unbind('click');
                        _this.display_picture($(this));
                    })
                }
            });
        })
    }

    $.fn.display_picture = function(image) {
        var _this = this;
        var image_container = image.find('.vignette');
        var width = parseInt(image_container.attr('data-width')), height = parseInt(image_container.attr('data-height'));
        var old_width = image_container.width(), old_height = image_container.height();
        var old_position = image.offset();
        var column = image.parents('.column').attr('id');
        var margin_left = 0;
        var columns = {
            left_column: null,
            center_column: null,
            right_column: null
            }, best_down = null, best_up = null;

        if (column == LEFT_COLUMN) {
            if(width >= MEDIUM_WIDTH) {columns[CENTER_COLUMN] = $('#' + CENTER_COLUMN);}
            if(width >= LARGE_WIDTH) {columns[RIGHT_COLUMN] = $('#' + RIGHT_COLUMN);}
        }
        if (column == CENTER_COLUMN) {
            if(width >= MEDIUM_WIDTH) {margin_left = -STEP; columns[LEFT_COLUMN] = $('#' + LEFT_COLUMN);}
            if(width >= LARGE_WIDTH) {margin_left = -STEP;columns[RIGHT_COLUMN] = $('#' + RIGHT_COLUMN);}
        }
        if (column == RIGHT_COLUMN) {
            if(width >= MEDIUM_WIDTH) {margin_left = -STEP; columns[CENTER_COLUMN] = $('#' + CENTER_COLUMN);}
            if(width >= LARGE_WIDTH) {margin_left = -STEP * 2; columns[LEFT_COLUMN] = $('#' + LEFT_COLUMN);}
        }
        best_down = _this.move_columns(columns, (old_position.top + old_height) / 2, 'down');
        best_up = _this.move_columns(columns, (old_position.top + old_height) / 2, 'up');

        if (parseInt(width) > 240) {
            image.removeClass('js-overlay')
            image.css('overflow', 'visible');
            image.find('.delete-photo').hide();
            image.find('.vignette-description').hide()

            image_container.css('z-index', 512);
            $('html, body').animate({scrollTop: image_container.offset().top - 200}, 500);
            for (var key in best_up) {var elt = best_up[key];if (elt == null){continue;}elt.parents('.column').children().first().animate({marginTop: -(elt.offset().top + elt.height() - old_position.top + ESCAPE_MARGIN)},500);}
            for (var key in best_down) {
                var elt = best_down[key];
                if (elt == null){continue;}
                elt.animate({
                    marginTop: height + ESCAPE_MARGIN * 2
                },{
                    duration:500,
                    complete: function() {
                        image_container.animate({
                            width: width,
                            height: height,
                            marginLeft: margin_left
                        }, 500);
                        _this.reduce_picture(image, old_width, old_height, best_down, best_up)
                    }
                });
            }
            if (best_down.left_column == null && best_down.center_column == null && best_down.right_column == null) {
                image_container.animate({
                    width: width,
                    height: height,
                    marginLeft: margin_left
                }, 500);
                _this.reduce_picture(image, old_width, old_height, best_down, best_up)
            }
        }
    }

    $.fn.add_picture = function(image) {
        var _this = this;
        var _min = null;
        $('#gallery .column').each(function() {
            var height = $(this).height();
            if (height == 0) {
                _min = $(this);
            } else if (_min == null || height < _min.height() ) {
                _min = $(this);
            }
        });
        _min.append(image.fadeIn(400));

        if (image.find('.vignette-expand').length > 0) {
            image.css('cursor', 'pointer');
            image.unbind('click').bind('click', function(event) {
                event.preventDefault()

                $('#gallery div.overlay').css('cursor', 'default')
                $('#gallery div.overlay').unbind('click');
                _this.display_picture($(this));
            });
        }
    }

    $.fn.gallery_init = function() {
        var _this = this;
        var images = Array();

        $('#gallery div.overlay img').each(function(index) {
            var img = $(this).attr('src', $(this).attr('data-url')).load(function() {
                if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) {
                    console.log('Broken image.')
                } else {
                    $(this).attr('data-height', this.naturalHeight);
                    $(this).attr('data-width', this.naturalWidth);
                }
            });
            _this.add_picture($(this).append(img).parent().hide())
        });

        $('.delete-photo').on('click', function(event) {
            var url = $(this).attr('href');
            var image = $(this).parent()
            event.preventDefault();
            event.stopPropagation();

            $('#popinDelete .validate').unbind('click').on('click', function() {
                $('#popinDelete').modal('hide');

                $.ajax({
                    url:url,
                    type: "GET",
                    success:function(data){
                        image.fadeOut(400, function() {
                            $(this).remove();
                        });
                    },
                    error:function (xhr, textStatus, thrownError){
                        console.log('error');
                    }
                });
            })

            $('#popinDelete').modal('toggle');
        })
    }

    $(this).gallery_init()

}(window.jQuery);