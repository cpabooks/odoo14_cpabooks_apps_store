odoo.define('cpabooks_community_sidebar.permanent', function (require) {
    "use strict";

    var Menu = require('web.Menu');
    var UserMenu = require('web.UserMenu');
    var session = require('web.session');
    var WebClient = require('web.WebClient');

    var menuWidget = null;

    function parseActionId(action) {
        if (!action) {
            return false;
        }
        var parts = String(action).split(',');
        return parts.length > 1 ? parseInt(parts[1], 10) : false;
    }

    function letterColor(name) {
        var colors = ['#0f766e', '#1d4ed8', '#7c3aed', '#be185d', '#c2410c', '#15803d', '#0369a1', '#4338ca'];
        var n = 0;
        var s = name || '';
        var i;
        for (i = 0; i < s.length; i++) {
            n = (n + s.charCodeAt(i)) % colors.length;
        }
        return colors[n];
    }

    function menuTree() {
        if (session.menu_data && session.menu_data.children && session.menu_data.children.length) {
            return session.menu_data.children;
        }
        if (menuWidget && menuWidget.menu_data && menuWidget.menu_data.children) {
            return menuWidget.menu_data.children;
        }
        return [];
    }

    function ensureChrome() {
        var $nav = $('.o_main_navbar').first();
        if (!$nav.length) {
            return false;
        }
        if (!$('.o_ccs_nav_btn').length) {
            $nav.find('.o_menu_apps').after(
                '<a href="#" class="o_ccs_nav_btn" title="Show default community menu bar">Default menu</a>'
            );
        }
        if (!$('.o_ccs_sidebar').length) {
            $nav.after(
                '<aside class="o_ccs_sidebar" role="navigation">' +
                '<div class="o_ccs_head">Apps</div>' +
                '<div class="o_ccs_search_wrap"><input type="search" class="o_ccs_search" placeholder="Search apps"/></div>' +
                '<nav class="o_ccs_apps"/></aside>'
            );
        }
        $('.o_ccs_sidebar').attr('data-ccs-ran', '1');
        return true;
    }

    function $leaf(menu, cls) {
        var actionId = parseActionId(menu.action);
        return $('<a href="#" class="' + cls + '"/>')
            .attr('title', menu.name)
            .attr('data-menu', menu.id)
            .attr('data-action-id', actionId || '')
            .append($('<span class="o_ccs_label"/>').text(menu.name));
    }

    function $nested(children) {
        var $box = $('<div class="o_ccs_subs2"/>');
        var i;
        for (i = 0; i < children.length; i++) {
            var child = children[i];
            if (child.children && child.children.length) {
                $box.append($nestedGroup(child));
            } else {
                $box.append($leaf(child, 'o_ccs_leaf'));
            }
        }
        return $box;
    }

    function $nestedGroup(menu) {
        var $g = $('<div class="o_ccs_sub_group"/>');
        var $tog = $('<a href="#" class="o_ccs_sub_toggle"/>')
            .attr('title', menu.name)
            .attr('data-menu', menu.id)
            .attr('data-action-id', parseActionId(menu.action) || '');
        $tog.append($('<span class="o_ccs_twisty fa fa-caret-right"/>'));
        $tog.append($('<span class="o_ccs_label"/>').text(menu.name));
        $g.append($tog);
        $g.append($nested(menu.children));
        return $g;
    }

    function $appRow(app) {
        var $wrap = $('<div class="o_ccs_group"/>').attr('data-menu-id', app.id);
        var $a = $('<a href="#" class="o_ccs_app"/>')
            .attr('title', app.name)
            .attr('data-menu-id', app.id)
            .attr('data-action-id', parseActionId(app.action) || '');
        $a.append(
            $('<span class="o_ccs_icon"/>').append(
                $('<span class="o_ccs_letter"/>')
                    .text((app.name || 'A').charAt(0).toUpperCase())
                    .css('background', letterColor(app.name))
            )
        );
        $a.append($('<span class="o_ccs_label"/>').text(app.name));
        var kids = app.children || [];
        if (kids.length) {
            $a.append($('<span class="o_ccs_caret fa fa-chevron-right"/>'));
        }
        $wrap.append($a);
        if (kids.length) {
            var $subs = $('<div class="o_ccs_subs"/>');
            var i;
            for (i = 0; i < kids.length; i++) {
                var child = kids[i];
                if (child.children && child.children.length) {
                    $subs.append($nestedGroup(child));
                } else {
                    $subs.append($leaf(child, 'o_ccs_sub'));
                }
            }
            $wrap.append($subs);
        }
        return $wrap;
    }

    function expandGroup($g, open) {
        $g.toggleClass('o_ccs_open', open);
        $g.find('> .o_ccs_app .o_ccs_caret').toggleClass('fa-chevron-down', open).toggleClass('fa-chevron-right', !open);
    }

    function fillSidebar() {
        if (!ensureChrome()) {
            return;
        }
        var $nav = $('.o_ccs_apps');
        if (!$nav.length) {
            return;
        }
        var apps = menuTree();
        if (!apps.length) {
            return;
        }
        if ($nav.children('.o_ccs_group').length === apps.length) {
            return;
        }
        $nav.empty();
        var i;
        for (i = 0; i < apps.length; i++) {
            $nav.append($appRow(apps[i]));
        }
        $('.o_ccs_sidebar').attr('data-ccs-apps', String(apps.length));
        var current = menuWidget && menuWidget.current_primary_menu;
        if (current) {
            var $cur = $nav.children('.o_ccs_group[data-menu-id="' + current + '"]');
            expandGroup($cur, true);
            $cur.children('.o_ccs_app').addClass('active');
        }
    }

    function bindOnce() {
        var $doc = $(document);
        if ($doc.data('ccsBound')) {
            return;
        }
        $doc.data('ccsBound', true);
        $doc.on('click.ccs', '.o_ccs_caret', function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $g = $(ev.currentTarget).closest('.o_ccs_group');
            expandGroup($g, !$g.hasClass('o_ccs_open'));
        });
        $doc.on('click.ccs', '.o_ccs_app', function (ev) {
            ev.preventDefault();
            var $el = $(ev.currentTarget);
            var $g = $el.closest('.o_ccs_group');
            $('.o_ccs_group').not($g).removeClass('o_ccs_open');
            $('.o_ccs_group').not($g).find('> .o_ccs_app .o_ccs_caret')
                .removeClass('fa-chevron-down').addClass('fa-chevron-right');
            expandGroup($g, true);
            var app = {
                menuID: parseInt($el.attr('data-menu-id'), 10),
                actionID: parseInt($el.attr('data-action-id'), 10),
            };
            if (menuWidget && menuWidget._appsMenu && menuWidget._appsMenu._openApp) {
                menuWidget._appsMenu._openApp(app);
            }
        });
        $doc.on('click.ccs', '.o_ccs_sub, .o_ccs_leaf', function (ev) {
            ev.preventDefault();
            var $el = $(ev.currentTarget);
            var menuId = parseInt($el.attr('data-menu'), 10);
            var actionId = parseInt($el.attr('data-action-id'), 10);
            $('.o_ccs_sub, .o_ccs_leaf').removeClass('active');
            $el.addClass('active');
            if (menuWidget && actionId) {
                menuWidget._on_secondary_menu_click(menuId, actionId);
            }
        });
        $doc.on('click.ccs', '.o_ccs_sub_toggle', function (ev) {
            ev.preventDefault();
            var $g = $(ev.currentTarget).closest('.o_ccs_sub_group');
            $g.toggleClass('o_ccs_open');
            var actionId = parseInt($(ev.currentTarget).attr('data-action-id'), 10);
            var menuId = parseInt($(ev.currentTarget).attr('data-menu'), 10);
            if (menuWidget && actionId) {
                menuWidget._on_secondary_menu_click(menuId, actionId);
            }
        });
        $doc.on('input.ccs', '.o_ccs_search', function () {
            var q = ($(this).val() || '').toLowerCase();
            $('.o_ccs_group').each(function () {
                var $g = $(this);
                var name = ($g.children('.o_ccs_app').attr('title') || '').toLowerCase();
                var hit = !q || name.indexOf(q) !== -1;
                if (!hit) {
                    $g.find('.o_ccs_label').each(function () {
                        if (($(this).text() || '').toLowerCase().indexOf(q) !== -1) {
                            hit = true;
                        }
                    });
                }
                $g.toggle(hit);
                if (hit && q) {
                    expandGroup($g, true);
                }
            });
        });
        $doc.on('click.ccs', '.o_ccs_nav_btn, .o_ccs_profile_default', function (ev) {
            ev.preventDefault();
            ev.stopImmediatePropagation();
            $('body').toggleClass('o_ccs_show_default_menu');
        });
    }

    function boot(menu) {
        if (menu) {
            menuWidget = menu;
        }
        bindOnce();
        fillSidebar();
    }

    Menu.include({
        start: function () {
            var self = this;
            menuWidget = this;
            var def = this._super.apply(this, arguments);
            boot(self);
            if (def && typeof def.then === 'function') {
                def.then(function () {
                    boot(self);
                });
            }
            setTimeout(function () { boot(self); }, 50);
            setTimeout(function () { boot(self); }, 400);
            setTimeout(function () { boot(self); }, 1500);
            return def;
        },
        change_menu_section: function (primary_menu_id) {
            this._super.apply(this, arguments);
            $('.o_ccs_app').removeClass('active');
            var $g = $('.o_ccs_group[data-menu-id="' + primary_menu_id + '"]');
            $g.children('.o_ccs_app').addClass('active');
            expandGroup($g, true);
        },
    });

    WebClient.include({
        show_application: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            var go = function () {
                boot(self.menu);
            };
            if (def && typeof def.then === 'function') {
                return def.then(function (res) {
                    go();
                    return res;
                });
            }
            go();
            return def;
        },
    });

    UserMenu.include({
        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            var inject = function () {
                if (!self.$('.o_ccs_profile_default').length) {
                    self.$('a[data-menu="logout"]').before(
                        $('<a/>', {
                            href: '#',
                            class: 'dropdown-item o_ccs_profile_default',
                            role: 'menuitem',
                        }).text('Default menu')
                    );
                }
                bindOnce();
            };
            inject();
            if (def && def.then) {
                return def.then(function (res) {
                    inject();
                    return res;
                });
            }
            return def;
        },
    });

    bindOnce();
});
