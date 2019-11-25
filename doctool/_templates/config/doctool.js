/** MIT License

 Copyright (c) 2019 Namgyal Brisson

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
 */
(function($, $doctoolSettings, $doctoolVersions) {
    function searchHandler(link, self) {
        var li = link.parent(),
            searchForm = $(self.searchForm),
            searchFormLis = searchForm.find('li'),
            textBox = $(self.searchTextBox);

        var text = link.text();
        if (text) {
            textBox.html(link.html() + " <i class=\"glyphicon glyphicon-filter\"></i>");
            searchForm.attr('action', self.baseHostUri + link.attr('data-target'));
            searchFormLis.removeClass('active');
            li.addClass('active');
        }
        else {
            // Get the first link in the list
            searchFormLis.addClass('active');
            searchForm.attr('action', self.baseHostUri + searchFormLis.find('a').attr('data-target'));
        }
    }

    var DoctoolApp = function() {
        var self = this;
        DoctoolApp.prototype.init = function(options) {

            self.options = options;
            self.location = window.location;
            self.body = 'body';

            self.debug = options.debug !== undefined ? options.debug : false;

            if (!self.debug) {
                console.log = function() {}
            }

            self.plusClass = "glyphicon-menu-right";
            self.minusClass = "glyphicon-menu-down";
            self.collapsibleMenu = ".collapsible-menu";

            self.content = '#content';
            self.container = '.container';

            self.contentImgs = self.container + ' img, ' + self.content + ' img';
            self.contentLinks = self.options.triggers !== undefined ? self.options.triggers : self.container + ' a, ' + self.content + ' a';
            self.panelLinks = '.panel-body a ';

            self.projectTocMenu = 'ul#menu';
            self.localTocMenu = '#panel ul:first-child';

            self.menuLinks = self.menu + ' a';
            self.navHomeLink = '#project-toc-menu';

            self.version = $doctoolSettings.version;
            self.availableVersions = $doctoolVersions;

            self.versionsUI = '#doctool-versions';
            self.availableVersionsUI = '#doctool-available-versions';
            self.versionLinksUI = '.version-link';

            self.localToc = '#panel';
            self.localTocObject = $(self.localToc);
            self.projectToc = '#accordion';
            self.navigationToc = '#doctool-projects-navigation';

            self.navigation = self.navigationToc + ' a, ' + self.projectToc + ' a';

            self.hides = self.projectToc + ', #doctool-search, #doctool-projects-navigation, .footer, ' + self.localToc;

            self.searchResults = '#search-results';
            self.searchTitle = '#search-documentation';

            self.searchForm = '#doctool-search-form';
            self.searchTextBox = '#doctool-search-text-box';
            self.searchFormLinks = self.searchForm + ' a';

            self.masterTitle = self.options.masterTitle !== undefined ? self.options.masterTitle : "";

            self.baseHostUri = (self.location + '').split(self.version)[0];

            if (!doctoolSettings.search) {
                searchHandler($('#all-projects-link'), self);
            }
            return self;
        };
        DoctoolApp.prototype.searchHandler = function(e) {
            return searchHandler($(this), self);
        };
        DoctoolApp.prototype.localTocHandler = function(e) {
            var tocItemsClasses = [];
            if(self.localTocObject.find('li').length <= 1) {
                self.localTocObject.remove();
            }
            else {
                var tocItemsList = self.localTocObject.find('ul');
                for(var i=0; i<tocItemsClasses.length; i++) {
                    var cls = tocItemsClasses[i];
                    tocItemsList.each(function(index) {
                        var item = $(this);
                        if(!item.hasClass(cls)) {
                            item.addClass(cls);
                        }
                    });
                }
            }
        };
        DoctoolApp.prototype.leftTocHandler = function(e) {
            var oldClass = self.plusClass;
            var newClass = self.minusClass;

            var glyph = $(this).children('.' + self.plusClass);
            if (glyph.length === 0) {
                glyph = $(this).children('.' + self.minusClass);
                oldClass = self.minusClass;
                newClass = self.plusClass;
            }

            if (glyph.length > 0) {
                glyph.removeClass(oldClass).addClass(newClass);
            }
        };
        DoctoolApp.prototype.setTocItemInitialState = function(item) {
            var link = item.attr('href'),
                attachedDiv = null,
                glyph = item.find('.glyphicon');

            if(link !== undefined) {
                attachedDiv = link.substr(0, 1) === "#" ? $(link) : null;
            }

            if(attachedDiv !== null ? attachedDiv.hasClass('in') : false) {
                glyph.removeClass(self.plusClass).addClass(self.minusClass);
            }
            else {
                glyph.removeClass(self.minusClass).addClass(self.plusClass);
            }
        };
        DoctoolApp.prototype.setLeftTocInitialStateHandler = function(e) {
            $(self.collapsibleMenu).each(function(index) {
                self.setTocItemInitialState($(this));
            });
        };
        DoctoolApp.prototype.getCurrentDocumentArgsString = function() {
            var url = self.location + '';
            return url.substring(url.indexOf('?') + 1);
        };
        DoctoolApp.prototype.getCurrentDocumentArgs = function() {
            return self._urlArgs2Array(self.location + '');
        };
        DoctoolApp.prototype._urlArgs2Array = function(url) {
            var request = {};
            var pairs = url.substring(url.indexOf('?') + 1).split('&');
            for (var i = 0; i < pairs.length; i++) {
                var pair = pairs[i].split('=');
                request[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1]);
            }
            return request;
        };
        DoctoolApp.prototype.getCurrentDocumentMode = function() {
            var args = self.getCurrentDocumentArgs();
            if(args.hasOwnProperty('mode'))
                return args.mode;
            return 'default';
        };
        DoctoolApp.prototype.documentModeHandler = function(e) {
            var mode = self.getCurrentDocumentMode();
            console.log('MODE : ' + mode);

            switch(mode) {
                case 'slide':
                case 'search':
                    $(self.hides).remove();
                    if(mode === 'search') {
                        var content = $(self.content),
                            searchResults = $(self.searchResults),
                            searchTitle = $(self.searchTitle),
                            searchResultsTitle = searchResults.find('h2').first();

                        content.find('p').remove();
                        content.find('.form-inline').first().remove();

                        if(searchResultsTitle.length > 0) {
                            searchResultsTitle.remove()
                        }

                        searchTitle.remove();
                    }
                    $('html, body').css({'margin': 0, 'padding': 0});
                    return true;
                default:
                    console.log('Unknown mode : ' + mode);
                    return false;
            }
        };
        DoctoolApp.prototype.targetBlankAllExternalLinksHandler = function(e) {
            var link = $(this).attr('href'),
                extension = link.split('.').pop(),
                isExternalLink = link.substr(0, 4) === "http" && !$doctoolSettings.host.test(link);

            if(isExternalLink) {
                e.preventDefault();
                e.stopPropagation();
                window.open(link);
            }
            else {
                switch(extension) {
                    case 'jpg':
                    case 'png':
                    case 'gif':
                    case 'zip':
                    case 'rar':
                    case 'pdf':
                        isExternalLink = true;
                        return false;
                }
            }
            return !isExternalLink;
        };
        DoctoolApp.prototype.targetBlankAllImagesHandler = function(e) {
            e.preventDefault();
            e.stopPropagation();
            window.open($(this).attr('src'));
            return false;
        };
        DoctoolApp.prototype.linkHandler = function(link) {
            if(link.substr(0, 1) === "#" || link.substr(0, 4) === "http") {
                return link;
            }
            return self.baseHostUri + link;
        };

        DoctoolApp.prototype.linksInitialStateHandler = function(e) {
            $(self.navigation).each(function(_) {
                $(this).attr('href', self.linkHandler($(this).attr('href')));
            });

            if(self.availableVersions.length <= 1) {
                $(self.versionsUI).hide();
            }
            else {
                var $versions = $(self.availableVersionsUI);
                var elements = (self.location + '').split(self.version);
                self.availableVersions.forEach(function (version) {
                    var link = [elements[0], version, elements[1]].join('');
                    var indexLink = [elements[0], version, '/index.html'].join('');
                    var anchor = $('<a href="#" class="version-link"><i class="glyphicon glyphicon-' + $doctoolSettings.home_icon + '"></i> ' + version + '</a>');
                    anchor.on('click', function (event) {
                        event.preventDefault();
                        $.get(link).then(function (response) {
                            console.log('response', response);
                            window.open(link, '_self');
                        }).catch(function (error) {
                            console.log('error', error);
                            window.open(indexLink, '_self');
                        });
                    });
                    $versions.append(
                        $('<li></li>').append(anchor)
                    )
                });
            }
        };
        DoctoolApp.prototype.onScrollTocHandler = function(e) {
            var scrollTop = '.5em';
            if($(this).scrollTop() === 0) {
                scrollTop = $(self.navigationToc).height() + 15 + 'px';
            }
            $(self.localToc + ', ' + self.projectToc).css('top', scrollTop);
        };
        DoctoolApp.prototype.MenuHeightHandler = function(e) {
            var winH = $(window).height(),
                navH = $(self.navigationToc).height(),

                rightPanel = $(self.localToc).find('.panel-body').first(),
                rightPanelHeadingH = $(self.localToc).find('.panel-heading').height(),
                rightPanelFooterH = $(self.localToc).find('.panel-footer').height(),

                rightH = winH - (navH + rightPanelHeadingH + rightPanelFooterH + 25),

                leftPanel = $(self.projectToc).find('.panel-body').first(),
                leftPanelHeadingH = $(self.projectToc).find('.panel-heading').height(),
                leftPanelFooterH = $(self.projectToc).find('.panel-footer').height(),

                leftH = winH - (navH + leftPanelHeadingH + leftPanelFooterH + 25);

            console.log('Window Height : ' + winH +
                ' Nav Height : ' + navH +
                ' Left Menu Height : ' + leftH +
                ' Right Menu Height : ' + rightH);

            leftPanel.css({'max-height': leftH + 'px', overflow: 'auto'});
            rightPanel.css({'max-height': rightH + 'px', overflow: 'auto'});
        };

        DoctoolApp.prototype.readyEventsHandler = function(e) {
            $(self.panelLinks).on('click', self.targetBlankAllExternalLinksHandler);
            $(self.contentLinks).on('click', self.targetBlankAllExternalLinksHandler);
            $(self.contentImgs).on('click', self.targetBlankAllImagesHandler);
            $(self.searchFormLinks).on('click', self.searchHandler);
            $(self.collapsibleMenu).on('click', self.leftTocHandler);

            $(window).on('scroll', self.onScrollTocHandler);
        };
        DoctoolApp.prototype.targetBlankForDownloads = function() {
            $('a.download').each(function(_) {
                $(this).attr('target', '_blank');
            });
        };
        DoctoolApp.prototype.attachEvents = function() {
            $(self.documentModeHandler);
            $(self.localTocHandler);
            $(self.setLeftTocInitialStateHandler);
            $(self.linksInitialStateHandler);
            $(self.readyEventsHandler);
            $(self.MenuHeightHandler);
            $(self.targetBlankForDownloads);
        };
    };
    new DoctoolApp().init({
        debug: $doctoolSettings.debug,
        masterTitle: $doctoolSettings.master_title,
    }).attachEvents();
})(jQuery, doctoolSettings, doctoolVersions);
