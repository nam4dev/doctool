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
    var DoctoolApp = function() {
        var self = this,
            Iframe = function(frameObject, contentDivId, pingInMs, debugMode) {
                var iframeSelf = this;

                iframeSelf.id = frameObject.attr('id');
                iframeSelf.currentHeight = frameObject.height();
                iframeSelf.previousHeight = 0;
                iframeSelf.contentDivId = contentDivId;
                iframeSelf.pingInMs = pingInMs;
                iframeSelf.debugMode = debugMode;
                iframeSelf.interval = null;
                iframeSelf.loader = '#' + iframeSelf.id + '-loader';

                if (iframeSelf.debugMode) {
                    console.log('Iframe ID : ' + iframeSelf.id + ' initialized');
                }
                iframeSelf._resizing = function() {
                    iframeSelf.currentHeight = frameObject.contents().find(iframeSelf.contentDivId).height() + 30;

                    if (iframeSelf.debugMode) {
                        console.log('Iframe ID : ' + iframeSelf.id + ' resizing from => ' +
                            iframeSelf.previousHeight + ' to => ' + iframeSelf.currentHeight + '... ');
                    }
                    if(iframeSelf.interval && iframeSelf.currentHeight === iframeSelf.previousHeight) {
                        clearInterval(iframeSelf.interval);
                        $(iframeSelf.loader).fadeOut(500);
                        if (iframeSelf.debugMode) {
                            console.log('Iframe ID : ' + iframeSelf.id +
                                ' fully resized (' + iframeSelf.currentHeight + 'px) !');
                        }
                    }
                    frameObject.height(iframeSelf.currentHeight);
                    iframeSelf.previousHeight = iframeSelf.currentHeight;
                };
                iframeSelf.resize = function() {
                    if (iframeSelf.debugMode) {
                        console.log('Iframe ID : ' + iframeSelf.id +
                            ' attaching interval event with : ' + iframeSelf.pingInMs + ' ms ...');
                    }
                    iframeSelf.interval = setInterval(iframeSelf._resizing, iframeSelf.pingInMs);
                    return iframeSelf;
                };
            };
        DoctoolApp.prototype.init = function(options) {
            self.options = options;
            self.location = window.location;

            self.debug = options.debug;

            self.iframes = 'iframe';
            self.loaders = 'img.loaders';
            self.searchResults = '#search-results';

            self.content = '#content';
            self.container = '.container';

            self.contentLinks = self.options.triggers !== undefined ? self.options.triggers : self.container + ' a, ' + self.content + ' a';
            self.panelLinks = '.panel-body a ';

            self.localToc = '#panel';
            self.navigationToc = '#doctool-projects-navigation';

            self.navigation = self.navigationToc + ' a';

            self.version = $doctoolSettings.version;
            self.availableVersions = $doctoolVersions;

            self.versionsUI = '#doctool-versions';
            self.availableVersionsUI = '#doctool-available-versions';
            self.versionLinksUI = '.version-link';

            self.searchForm = '#doctool-search-form';
            self.searchTextBox = '#doctool-search-text-box';
            self.searchFormLinks = self.searchForm + ' a';
            self.masterTitle = self.options.masterTitle !== undefined ? self.options.masterTitle : "";
            self.baseHostUri = (self.location + '').split(self.version)[0];

            self.setCurrentSearchArgs();
            self.setIframeSources();

            return self;
        };
        DoctoolApp.prototype.searchHandler = function(e) {
            var link = $(this),
                li = link.parent(),
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
        };
        DoctoolApp.prototype.getCurrentDocumentArgsString = function() {
            var url = self.location + '';
            return url.substring(url.indexOf('?') + 1);
        };
        DoctoolApp.prototype.setIframeSources = function() {
            $(self.searchResults).fadeOut(0);
            $(self.iframes).each(function(index) {
                var iframe = $(this),
                    iframeSrc = iframe.attr('src');
                iframe.attr('src', iframeSrc + '&' + self.getCurrentDocumentArgsString());
            });
        };
        DoctoolApp.prototype.targetBlankAllExternalLinksHandler = function(e) {
            var link = $(this).attr('href'),
                extension = link.split('.').pop(),
                isExternalLink = link.substr(0, 4) === "http" && !$doctoolSettings.host.test(link);

            if(!isExternalLink) {
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

            if(isExternalLink) {

                e.preventDefault();
                e.stopPropagation();

                window.open(link);
            }
            return !isExternalLink;
        };
        DoctoolApp.prototype.iframeHandler = function(e) {
            var iframe = new Iframe($(this), self.searchResults, 250, self.debug);
            iframe.resize();
            $(self.searchResults).fadeIn(500);
            $(self.loaders).fadeIn(500);
        };
        DoctoolApp.prototype.onScrollTocHandler = function(e) {
            var scrollTop = '.5em';
            if($(this).scrollTop() === 0) {
                scrollTop = $(self.navigationToc).height() + 15 + 'px';
            }
            $(self.localToc).css('top', scrollTop);
        };
        DoctoolApp.prototype.linkHandler = function(link) {
            if(link.substr(0, 1) === "#" || link.substr(0, 4) === "http") {
                return link;
            }
            return self.baseHostUri + link;
        };
        DoctoolApp.prototype.linksInitialStateHandler = function(e) {
            $(self.navigation).each(function(index) {
                var link = $(this).attr('href');
                if (link) {
                    $(this).attr('href', self.linkHandler(link));
                }
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
        DoctoolApp.prototype.setCurrentSearchArgs = function() {
            var args = self.getCurrentDocumentArgs();
            if(args.hasOwnProperty('q')) {
                $('input[name=q]').val(args.q);
            }
        };
        DoctoolApp.prototype.readyEventsHandler = function(e) {
            $(self.panelLinks).on('click', self.targetBlankAllExternalLinksHandler);
            $(self.contentLinks).on('click', self.targetBlankAllExternalLinksHandler);
            $(self.searchFormLinks).on('click', self.searchHandler);
            $(self.iframes + '.iframe-frame').on('load', self.iframeHandler);
            $(window).on('scroll', self.onScrollTocHandler);
        };
        DoctoolApp.prototype.attachEvents = function() {
            $(self.linksInitialStateHandler);
            $(self.readyEventsHandler);
        };
    };
    new DoctoolApp().init({
        debug: $doctoolSettings.debug,
        masterTitle: $doctoolSettings.master_title
    }).attachEvents();
})(jQuery, doctoolSettings, doctoolVersions);
