!function($){

    "use strict";

    var Gallery = function(data) {
        this.owner = data.owner;
        this.name = data.name;
        this.slug = data.slug;
        this.count = data.count;
    }

    var SearchBar = function(element, options) {
        this.element = element;
        this.limit = Infinity;
        this.galleries = [];

        var data = JSON.parse(element.attr('data-dict'));
        for (var i = 0; i < data.length; i++) {
            this.galleries.push(new Gallery(data[i]));
        }
        element.removeAttr('data-dict');
        this.options = options;

        this.init_listeners();
    }

    SearchBar.prototype.init_listeners = function() {
        // DOM initialisation with elements we need
        this.element.attr('autofocus', true)
        this.element.empty();
        this.element.parent().append(this.options.hint);
        this.element.insertAfter($('.tt-hint'));
        this.element.parent().append(this.options.menu);
        this.dropdown = this.element.next($.parseHTML(this.options.menu).class).hide();
        this.hint = $('.tt-hint');

        var that = this;

        // Listener on input
        this.element.on('input', function() {
            var input = $(this).val()

            if (input.length == 0) {
                that.hint.val('');
                return that.dropdown.slideUp(400);
            }

            var galleries_header = that.find_galleries(input);
            if (galleries_header.matching.length == 0) {
                that.dropdown.slideUp(400);
                that.hint.val('');
                return;
            }
            if (that.display_in_dropdown(galleries_header.matching, galleries_header.owners_header)) {
                that.dropdown.slideDown(400);
            }
            that.active_next();
        }).focus(function() {
            return !that.input_is_empty() && that.dropdown.slideDown(400);
        }).blur(function() {
            that.dropdown.slideUp(400);
        }).keydown(function(e) {
            var keyCode = e.keyCode || e.which;

            if (that.dropdown.children().length == 0 || that.input_is_empty()) {
                return 0;
            }
            if (keyCode == 40 || keyCode == 9) {
                e.preventDefault();
                that.active_next();
            } else if (keyCode == 38) {
                e.preventDefault();
                that.active_previous();
            } else if (keyCode == 13) {
                e.preventDefault();
                return that.redirect_gallery(that.get_gallery_active());
            }
        });
    }

    SearchBar.prototype.find_galleries = function(input) {
        var re = new RegExp(input.toLowerCase());
        var galleries = this.galleries;
        var matching = [];
        var owners = [];

        for (var i = 0; i < galleries.length; i++) {
            if (galleries[i].name.toLowerCase().match(re)) {
                if (matching.indexOf(galleries[i]) == -1) {
                    matching.push(galleries[i]);
                }
                if (owners.indexOf(galleries[i].owner) == -1) {
                    owners.push(galleries[i].owner);
                }
            }
            if (galleries[i].owner.toLowerCase().match(re)) {
                for (var j = 0; j < galleries.length; j++) {
                    if (galleries[j].owner == galleries[i].owner && matching.indexOf(galleries[j]) == -1) {
                        matching.push(galleries[j]);
                    }
                }
                if (owners.indexOf(galleries[i].owner) == -1) {
                    owners.push(galleries[i].owner);
                }
            }
            if (matching.length >= this.limit) {
                break;
            }
        }
        return {matching: matching, owners_header: owners};
    }

    SearchBar.prototype.display_in_dropdown = function(matching, headers) {
        this.dropdown.empty();

        for (var i = 0; i < headers.length; i ++) {
            this.dropdown.append($('<h2>').html(this.options.header).find('h2').append('<a href="/gallery/' + headers[i] + '">' + headers[i] + '</a>'));
            for (var j = 0; j < matching.length; j++) {
                if (matching[j].owner == headers[i]) {
                    this.dropdown.append($('<span>').html(this.options.item).find('span').append(this.format_suggestions(matching[j])).attr('data-index', this.galleries.indexOf(matching[j])));
                }
            }
        }
        var that = this;
        $('.tt-suggestions', this.dropdown).hover(function() {
            that.set_active($(this));
        });
        return true;
    }

    SearchBar.prototype.format_suggestions = function(gallery){
        var word = ' photo';
        if (gallery.count > 0) word += 's';
        return '<p>' + gallery.name + '<span class="badge">' + gallery.count + '</span></p>';
    }

    SearchBar.prototype.format_header = function(gallery) {
        return gallery.owner;
    }

    SearchBar.prototype.active_next = function() {
        var active = this.dropdown.find('.active');
        var items = $('.tt-suggestions', this.dropdown);
        var index = 0;

        for (var i = 0; i < items.length; i++) {
            if (items.eq(i).hasClass('active')) {
                index = (i + 1) % items.length;
            }
        }
        active.removeClass('active');
        items.eq(index).addClass('active');
        this.dropdown.get(0).scrollTop = items.eq(index).position().top - this.dropdown.offset().top - 46;

        this.display_hint(this.get_active());
    }

    SearchBar.prototype.active_previous = function() {
        var active = this.dropdown.find('.active');
        var items = $('.tt-suggestions', this.dropdown);
        var index = items.length - 1;

        for (var i = 0; i < items.length; i++) {
            if (items.eq(i).hasClass('active')) {
                if (i - 1 >= 0) {
                    index = (i - 1);
                }
            }
        }
        active.removeClass('active');
        items.eq(index).addClass('active');
        this.dropdown.get(0).scrollTop = items.eq(index).position().top - this.dropdown.offset().top + 46;
        this.display_hint(this.get_active());
    }

    SearchBar.prototype.is_active = function() {
        if ($('.active', this.dropdown).length == 1) {
            return true;
        }
        return false;
    }

    SearchBar.prototype.input_is_empty = function() {
        return this.element.val() == '';
    }

    SearchBar.prototype.set_active = function(gallery) {
        $('.active', this.dropdown).removeClass('active');
        var that = this;
        gallery.addClass('active').click(function () {
            return that.redirect_gallery(that.get_gallery_active());
        });
        this.display_hint(this.get_active());
        return;
    }

    SearchBar.prototype.get_active = function() {
        var index = $('.active', this.dropdown).attr('data-index');

        if (index == undefined) return

        var gallery = this.galleries[index];
        var input = this.element.val();
        var name_result = '', owner_result = '';
        var owner_end = Infinity, name_end = 0;

        for (var i = 0; i < gallery.owner.length; i++) {
            if (input[i] != undefined && input[i].toLowerCase() == gallery.owner[i].toLowerCase()) {
                owner_result += input[i];
            } else {
                owner_end = i;
                owner_result += gallery.owner.slice(i, gallery.owner.length);
                break;
            }
        }
        for (var i = 0; i < gallery.name.length; i++) {
            if (input[i] != undefined && input[i].toLowerCase() == gallery.name[i].toLowerCase()) {
                name_result += input[i];
            } else {
                name_end = i
                name_result += gallery.name.slice(i, gallery.name.length)
                break;
            }
        }
        if (owner_end == Infinity) return '';
        if (name_end == 0) return '';

        return (owner_end > name_end) ? owner_result : name_result;
    }

    SearchBar.prototype.get_gallery_active = function() {
        if (this.is_active()) {
            return this.galleries[$('.active', this.dropdown).attr('data-index')];
        }
    }

    SearchBar.prototype.display_hint = function(hint) {
        if (this.is_active()) {
            this.hint.val(hint);
        }
    }

    SearchBar.prototype.redirect_gallery = function(gallery) {
        $.ajax({
            url:$('section#home > form').attr('data-url'),
            type: "POST",
            data: gallery,
            success:function(data){
                window.location.href = data.redirect;
            },
            complete:function(){},
            error:function (xhr, textStatus, thrownError){

            }
        });
    }

    var options = {
        menu: '<div class="tt-dropdown-menu"></div>',
        item: '<span class="tt-suggestions"></span>',
        hint: '<input class="tt-hint" type="text" autocomplete="off" disabled">',
        header: '<h2 class="gallery-owner"></h2>'
    }

    var searchbar = new SearchBar($('#id_search'), options);

}(window.jQuery);