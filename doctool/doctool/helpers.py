#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Namgyal BRISSON (nam4dev)"
__since__ = "10/25/2019"
__copyright__ = """MIT License

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
"""

"""
:summary: Groups all Project's Utility Classes
"""
import os
import re
import json
import shutil
import logging
import functools
import traceback
import subprocess
import collections

from doctool import settings
from doctool import errors

logger = logging.getLogger(__name__)


def run_command(command, shell=None, cwd=".", env=None):
    """
    Run a command on the local system.

    ``shell`` is passed directly to `subprocess.Popen
    <http://docs.python.org/library/subprocess.html#subprocess.Popen>`_'s
    ``execute`` argument (which determines the local shell to use.)  As per the
    linked documentation, on Unix the default behavior is to use ``/bin/sh``,
    so this option is useful for setting that value to e.g ``/bin/bash``.

    :param command: The command-line to execute
    :type command: str

    :param shell: See :mod:`subprocess.Popen`
    :type shell: object

    :param cwd: The current directory to execute the command
    :type cwd: str

    :param env: The OS Environment dictionary
    :type env: dict

    :return: A Attribute String object containing all data about just run command
    :rtype: Types.AttributeString
    """
    logger.debug("[subprocess]: " + command)
    try:
        if cwd:
            command = "cd {0} && {1}".format(cwd, command)

        cmd_arg = command if settings.IS_WINDOWS else [command]
        options = dict(shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if shell is not None:
            options['executable'] = shell

        pop = subprocess.Popen(cmd_arg, **options)
        stdout, stderr = pop.communicate()
    finally:
        pass

    # Handle error condition (deal with stdout being None, too)
    out = Types.AttributeString(str(stdout.strip(), 'utf8') if stdout else b'')
    err = str(stderr.strip() if stderr else b'', 'utf8')
    rcode = pop.returncode

    out.failed = False
    out.rcode = rcode
    out.stderr = err

    if rcode != 0:
        out.failed = True
        msg = "run_command() encountered an error (return code %s) while executing '%s'" % (rcode, command)
        msg += '\n' + (err if err else out)
        logger.exception(msg)

    out.succeeded = not out.failed

    try:
        log_file = os.path.join(os.path.expanduser('~'), 'doctool.log')
        with open(log_file, 'w') as writer:
            writer.write(out)
            writer.write(out.stderr)
    except Exception:
        pass

    return out


def exception(func):
    """
    decorator to encapsulate the exception
    behavior for a given function

    :param func: The function to decorate

    :return: The wrapped function
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        status = False
        try:
            func(*args, **kwargs)
            status = True
        except errors.SysErrors:
            logger.exception(
                'Error while calling `{}` '
                'with args: {} & kwargs: {}'.format(func.__name__, args, kwargs)
            )
        return status
    return wrapped


class ProjectHelper(object):
    """
    This Class groups some helper methods for the :class:`ProjectManager`
    """

    copy = staticmethod(shutil.copy2)
    run_command = staticmethod(run_command)

    @classmethod
    def __cptree(cls, src, dst, symlinks=False, ignore=None):
        """
        Recursively copy a directory tree using copy2().

        The destination directory must not already exist.
        If exception(s) occur, an Error is raised with a list of reasons.

        :param src: source files directory path
        :type src: str

        :param dst: output directory path
        :type dst: str

        :param symlinks: If the optional symlinks flag is true, symbolic links in the
            source tree result in symbolic links in the destination tree; if
            it is false, the contents of the files pointed to by symbolic
            links are copied.

        :type symlinks: bool

        :param ignore: The optional ignore argument is a callable. If given, it
            is called with the `src` parameter, which is the directory
            being visited by copytree(), and `names` which is the list of
            `src` contents, as returned by os.listdir():

                callable(src, names) -> ignored_names

            Since copytree() is called recursively, the callable will be
            called once for each directory that is copied. It returns a
            list of names relative to the `src` directory that should
            not be copied.

        :type ignore: callable
        """
        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        cls.createdirs(dst)
        errors_ = []
        for name in names:
            if name in ignored_names:
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    cls.__cptree(srcname, dstname, symlinks=symlinks, ignore=ignore)
                else:
                    shutil.copy2(srcname, dstname)
                    # XXX What about devices, sockets etc.?
            except (IOError, os.error) as why:
                errors_.append((srcname, dstname, str(why)))
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except shutil.Error as err:
                errors_.extend(err.args[0])
        try:
            shutil.copystat(src, dst)
        except OSError as why:
            if hasattr(shutil, 'WindowsError') and isinstance(why, shutil.WindowsError):
                # Copying file access times may fail on Windows
                pass
            else:
                errors_.extend((src, dst, str(why)))
        if errors_:
            raise shutil.Error(errors_)

    @classmethod
    def load_from_file(cls, configuration):
        """
        Loads from filesystem the configuration file into memory.

        :param configuration: The Configuration minimal data got from the global Configuration file.
        :type configuration: dict

        :return: The configuration data
        :rtype: Types.AttributeDict
        """
        conf = {}
        conf.update(configuration)
        project_dir = conf.get('dir2parse')
        uid = conf.get('id') or project_dir
        assert project_dir is not None, errors.ConfigurationError('Please fill in your project root directory for '
                                                                  'project key : {0} ! '.format(uid))
        if not os.path.isdir(project_dir):
            project_dir = ProjectHelper.absjoin(conf.get('working_dir', settings.REPO_BASE), project_dir)
        assert os.path.isdir(project_dir), errors.ConfigurationError(
            'Please ensure your project root directory exists for project key : {0} ! '.format(uid)
        )
        project_conf_filename = ProjectHelper.absjoin(project_dir, 'doctool_settings.json')
        if os.path.isfile(project_conf_filename):
            with open(project_conf_filename, 'r') as handle:
                conf.update(json.loads(handle.read()))
        else:
            logger.warning('The project {0} has no configuration file (doctool_settings.json) !'.format(uid))
        # Important: Overriding the dir2parse with computed project_dir
        # When relative path is used, the resulting project directory is an absolute and normed path.
        conf['dir2parse'] = project_dir
        return Types.AttributeDict(conf)

    @classmethod
    def exists(cls, val):
        """
        Checks if the given value is valid as a path

        :param val: the path to validate
        :type val: str or Types.AttributeString

        :return: Validity status
        :rtype: bool
        """
        return val and os.path.exists(val)

    @classmethod
    def which(cls, program):
        """
        Emulates Unix like Which Command on Windows.

        :param program: The program to be found
        :type program: str

        :return: The executable path
        :rtype: Types.AttributeString
        """
        def is_exe(filepath):
            """
            Tells if a given path is executable or not.

            :param filepath:
            :type filepath: str

            :return: Whether or not the given file si an executable or not.
            :rtype: bool
            """
            return os.path.isfile(filepath) and os.access(filepath, os.X_OK)

        ret = None
        if settings.IS_WINDOWS:
            if not program.endswith('.exe'):
                program = '{0}.exe'.format(program)

            fpath, fname = os.path.split(program)
            if fpath:
                if is_exe(program):
                    ret = program
            else:
                for path_ in os.environ["PATH"].split(os.pathsep):
                    path_ = path_.strip('"')
                    exe_file = os.path.join(path_, program)
                    if is_exe(exe_file):
                        ret = exe_file

        out = Types.AttributeString(ret.strip() if ret else "")
        out.succeeded = is_exe(out)
        out.failed = not out.succeeded

        return out

    @classmethod
    def get_executable_path(cls, executable_name):
        """
        Gets the executable path, if installed.

        :param executable_name: The executable name
        :type executable_name: str

        :return: The executable path
        :rtype: Types.AttributeString
        """
        if settings.IS_WINDOWS:
            return cls.which(executable_name)
        return cls.run_command('which {0}'.format(executable_name), cwd="", env=os.environ.copy())

    @classmethod
    def slugify(cls, slug):
        """
        Slugify a given String as so :

        my_text = 'Toto is not very clever'
        slugify(my_text)

        Gives you :

        'toto-is-not-very-clever'

        :param slug: The String to be slugify
        :type slug: str or unicode

        :return: The Slug of the passed String
        :rtype: unicode
        """
        slug = slug.lower()
        return re.sub(r'\W+', '-', slug)

    @classmethod
    def read_file(cls, fname, mode='r', readlines=True):
        """
        Reads content to the given filename

        :param fname: filename
        :type fname: str

        :param mode: wraps builtin :meth:`open` mode
        :type mode: str
        """
        if not os.path.isfile(fname):
            raise errors.InvalidParameterError('The given filename : {0} does NOT exists !'.format(fname))

        logger.debug('Reading file {0}.'.format(fname))
        with open(fname, mode) as f:
            content = f.readlines() if readlines else f.read()
        return content

    @classmethod
    def write_file(cls, fname, content, mode='wb', override=False):
        """
        Writes content to the given filename

        :param override: if set, file is overridden
        :type override: bool

        :param fname: filename
        :type fname: str

        :param content: content to write
        :type content: str or tuple or list

        :param mode: wraps builtin :meth:`open` mode
        :type mode: str
        """
        if override or not os.path.isfile(fname):
            logger.debug(
                '{1} file {0}.'.format(
                    fname, 'Overriding'
                    if override and os.path.isfile(fname)
                    else 'Creating'
                )
            )
            with open(fname, mode) as f:
                if isinstance(content, (tuple, list)):
                    content = '\n'.join(content)

                if not isinstance(content, bytes):
                    content = bytes(content, 'utf8').decode()
                f.write(content)
        else:
            logger.debug('File {0} already exists, skipping.'.format(fname))

    @classmethod
    def cptree(cls, source, destination, symlinks=False, ignore=None):
        """
        Copy recursively a tree from the source directory to the destination directory

        :param symlinks: Whether symbolic link may be processed
        :type symlinks: bool

        :param ignore: A callable to handle ignored cases
        :type ignore: callable

        :param source: The source to copy
        :type source: str

        :param destination: The destination where to copy
        :type destination: str
        """
        if os.path.exists(source) and os.path.isdir(source):
            try:
                cls.__cptree(source, destination, symlinks=symlinks, ignore=ignore)
            except (errors.SysErrors, shutil.Error) as exc:
                logger.exception(exc)

    @classmethod
    def rmtree(cls, directory_path):
        """
        Removes a given directory tree

        :param directory_path: The logical directory path to be created
        :type directory_path: str or unicode
        """
        rmtree = exception(shutil.rmtree)
        status = rmtree(directory_path)
        if status:
            output = ('REMOVING TREE => ``{0}`` ...'.format(directory_path))
        else:
            output = traceback.format_exc()
        logger.debug(output)
        return status

    @classmethod
    def createdirs(cls, directory_path):
        """
        Creates a given directory tree recursively

        :param directory_path: The logical directory path to be created
        :type directory_path: str or unicode
        """
        status = False
        if not os.path.exists(directory_path):
            makedirs = exception(os.makedirs)
            status = makedirs(directory_path, exist_ok=True)
            if status:
                logger.debug('CREATING DIRECTORY => ``{0}`` ...'.format(directory_path))
        return status

    @classmethod
    def handle_path(cls, relpath, basedir=""):
        """
        Manage ``WORKING_DIR`` JSON configuration field.
        If this field is provided all path's data found in configuration file are checked.

        If the provided path exists (:meth:`os.path.exists`), then the path is returned as is.
        Otherwise, a normalized path is returned with WORKING_DIR concatenated to relative path.

        .. note:: repo default configuration

        :type relpath: str
        :param relpath: relative or absolute path.

        :type basedir: str
        :param basedir: Optional base directory (to be concatenated).

        :return: The proper path
        :rtype: str
        """
        abspath = r'{0}'.format(relpath) if relpath is not None else ""
        # This a hack for :func:`os.path.exists`
        # which return true if the path does not start by os.sep
        if abspath and not abspath.startswith('{0}'.format(os.sep)):
            abspath = r'{0}{1}'.format(os.sep, abspath)

        if abspath and not os.path.exists(abspath):
            # Getting back the initial value (hack)
            if abspath.startswith('{0}'.format(os.sep)):
                abspath = abspath[len(os.sep):]
            abspath = r'{0}'.format(cls.absjoin(basedir or settings.REPO_BASE, abspath))

        return abspath

    @classmethod
    def absjoin(cls, *args):
        """
        Custom join + abspath

        .. note:: :meth:`os.path.abspath` method calls :meth:`os.path.normpath` method. Therefore, there's no need to
            call it after the absjoin method.

        :param args: Non Keyword arguments to be joined together
        :type args: tuple, list

        :return: An absolute & normed joined path
        :rtype: str
        """
        return settings.absjoin(*args)

    @classmethod
    def normpath(cls, path):
        """
        Norm a path as Unix-like separator

        :param path: The path
        :type path: str

        :return: The normed path
        :rtype: str
        """
        return settings.normpath(path)

    @classmethod
    def split_all(cls, filename, no_sep=True, debug=False):
        """
        Cross-platform filename Splitter utility.

        :func:`os.path.split`, Split a pathname.

        It returns tuple (head, tail) where tail is everything after the final slash.
        Either part may be empty.

        But the aims of this function is to **really do a full split** on given filename.

        Let's take a basic example:
            C:/dir1/dir2/.../dir10/document.pdf

            will output:
                * with :func:`os.path.split` -> ["C:/dir1/dir2/.../dir10", "document.pdf"]
                * with :func:`self.full_split` -> ["C:", "/dir1", "/dir2", "/...", "/dir10", "document.pdf"]

        .. note:: if `no_sep` is True the output is -> ["C:", "dir1", "dir2", "...", "dir10", "document.pdf"]

        :param filename: the filename to be split
        :type filename: str

        :param no_sep: Do not include path separators in the split (default is True)
        :type no_sep: bool

        :param debug: if True, some prints are enabled (default is False)
        :type debug: bool

        :return: The split filename components
        :rtype: list
        """
        components = []
        if no_sep:
            while True:
                filename, tail = os.path.split(filename)
                if tail == "":
                    components.reverse()
                    break
                components.append(tail)
        else:
            while True:
                new, tail = os.path.split(filename)
                if debug:
                    logger.debug(repr(filename), (new, tail))
                if new == filename:
                    assert not tail
                    if filename:
                        components.append(filename)
                    break
                components.append(tail)
                filename = new
            components.reverse()
        return components

    @classmethod
    def replace_extension(cls, filename, new_extension, extension=None):
        """
        Replaces the filename extension.

        :param filename: The filename which need to have its extension replaced
        :type filename: str

        :param new_extension: The new filename extension
        :type new_extension: str

        :param extension: (optional) The logical current filename extension
        :type extension: str

        :return: The modified filename
        :rtype: str
        """
        if not extension:
            extension = filename.split('.')[-1]

        if not str(extension).startswith('.'):
            extension = '.' + extension

        if not str(new_extension).startswith('.'):
            new_extension = '.' + new_extension

        if filename.endswith(extension):
            filename = filename.replace(extension, new_extension)

        return filename

    @classmethod
    def remove(cls, guess):
        """
        Removes the given directory or filename
        """

        if os.path.isdir(guess):
            cls.rmtree(guess)
        elif os.path.isfile(guess):
            try:
                os.unlink(guess)
            except errors.SysErrors as exc:
                logger.exception('Filename : [0} failed to be removed for those reasons : \n{1}'.format(guess, exc))


class CodeProjectHelper(ProjectHelper):
    """
    This Class groups some API helper methods for the :class:`ProjectManager`
    """


class Types(object):
    """
    Groups some Useful Custom Types

        * AttributeString
        * AttributeDict
    """
    OrderedDict = collections.OrderedDict

    class AttributeString(str):
        """
        String subclass which allows arbitrary attribute access.
        """

    class AttributeDict(OrderedDict):
        """
        Dictionary subclass enabling attribute lookup/assignment of keys/values.

        For example::

            >>> m = Types.AttributeDict({'foo': 'bar'})
            >>> m.foo
            'bar'
            >>> m.foo = 'not bar'
            >>> m['foo']
            'not bar'

        ``_AttributeDict`` objects also provide ``.first()`` which acts like
        ``.get()`` but accepts multiple keys as arguments, and returns the value of
        the first hit, e.g.::

            >>> m = Types.AttributeDict({'foo': 'bar', 'biz': 'baz'})
            >>> m.first('wrong', 'incorrect', 'foo', 'biz')
            'bar'
        """

        def __getattr__(self, key):
            # The attribute access is allowed only for public members
            # Protected & Private ones are treated as normal instance attributes
            if not key.startswith('_'):
                try:
                    return self[key]
                except KeyError:
                    # to conform with __getattr__ spec
                    raise AttributeError(key)
            else:
                # Default behavior
                return super(Types.AttributeDict, self).__getattribute__(key)

        def __setattr__(self, key, value):
            # The attribute access is allowed only for public members
            # Protected & Private ones are treated as normal instance attributes
            if not key.startswith('_'):
                self[key] = value
            else:
                # Default behavior
                return super(Types.AttributeDict, self).__setattr__(key, value)

        def first(self, *names):
            """
            acts like
            ``.get()`` but accepts multiple keys as arguments, and returns the value of
            the first hit, e.g.::

                >>> m = Types.AttributeDict({'foo': 'bar', 'biz': 'baz'})
                >>> m.first('wrong', 'incorrect', 'foo', 'biz')
                'bar'

            :param names: Multiple keys tuple
            :type names: tuple

            :return: The value of the first hit
            """
            for name in names:
                value = self.get(name)
                if value:
                    return value

    class KeyList(list):

        def __init__(self, sequence=None, key='id'):
            """
            Constructor

            :param sequence: The initial sequence a list takes
            :type sequence: list or tuple

            :param key: The key of the list
            :type key: str
            """
            super(Types.KeyList, self).__init__(sequence or ())
            self._key = key
            self.uid_index = {}

            if sequence:
                for item in sequence:
                    self.uid_index[item.get(key)] = item

        def append(self, item):
            """
            Append an item

            :param item: Any item
            """
            super(Types.KeyList, self).append(item)
            self.uid_index[item.get(self._key)] = item

        def __contains__(self, uid):
            contained = super(Types.KeyList, self).__contains__(uid)
            if not contained:
                contained = uid in self.uid_index
            return contained

        def get(self, uid):
            """
            Get an item by its UID

            :param uid: The item's UID

            :return: The item
            """
            return self.uid_index.get(uid)

    class TOCList(list):
        """
        Represents a collection of TOCItem instances
        """
        __IS_HIDDEN = False

        GLOBAL_ID = 0
        RST_TITLE_TYPOS = ('#', '*', '-', '^', '~', '=', '"')
        RST_ALL_TYPOS = RST_TITLE_TYPOS + ('..', ':')

        @classmethod
        def seek_for_title_info(cls, lines, symbols):
            """
            Method seeking for each symbol pattern provided by the symbols argument
            into the given lines using :meth:`str.startswith`.
            When a symbol is found at the start of a line,
            a boolean set to true, the index and the symbol are returned

            :type lines: list or tuple
            :param lines: The lines contained into a file

            :type symbols: list or tuple
            :param symbols: A list of symbols to seek for

            :rtype: tuple[bool, int]
            :return: a boolean and the index in the lines
            """
            for index, line in enumerate(lines):
                stripped = line.strip()
                if not stripped:
                    continue

                for symbol in symbols:
                    if stripped.startswith(symbol):
                        return True, index, symbol
            return False, -1, ''

        @property
        def first_link(self):
            """
            Finds the first valid link from the TOC
            to get this link showed when opening the documentation

            :return: The first found link or empty string
            :rtype: str
            """
            if not self._first_link:
                self._first_link = self._recurse_over_links(self.items)
            return self._first_link

        @property
        def items(self):
            """
            Property for the inner Items list

            :return: The inner Items list
            :rtype: list
            """
            return list(self.__items)

        def __init__(self, sequence=None,
                     src_dirname="",
                     suffix="",
                     maxdepth=3,
                     master_name='index',
                     master_name_excluded=True,
                     joined_stripped=False,
                     is_api=False):
            """
            Constructor

            :param sequence: A list to init this one
            :type sequence: tuple or list
            """
            sequence = sequence or []
            super(Types.TOCList, self).__init__(sequence)

            self._is_api = is_api

            self.__main_dict = collections.OrderedDict()
            self.__items = Types.KeyList(key='hash')
            self.__analysis_list = []
            self.__alias = {}

            self._first_link = ""
            self._current_depth = 0
            self._basepath = src_dirname
            self._suffix = suffix
            self._maxdepth = maxdepth
            self._master_name = master_name
            self._master_name_excluded = master_name_excluded
            self._joined_stripped = joined_stripped

        def _get_title_from_rst_file(self, rst_file):
            """
            Get the title from a RST file (following RST convention)

            :type rst_file: str
            :param rst_file: The RST file path

            :rtype: str
            :return: The found title (stripped)
            """
            title = '@doctool.missing.title'
            try:
                with open(rst_file, 'rb') as page:
                    lines = [str(l, 'utf8') for l in page.readlines()]
                    found, index, symbol = self.seek_for_title_info(lines, self.RST_TITLE_TYPOS)
                    if found:
                        if lines[index + 2].startswith(symbol):
                            title = str(lines[index + 1]).strip()
                        else:
                            title = str(lines[index - 1]).strip()
            except (errors.SysErrors, Exception):
                logger.debug('Resolving RST file {0} title failed !'.format(rst_file))
                logger.debug(traceback.format_exc())

            return title.strip()

        def _recurse_over_links(self, toc):
            """
            Recursive inner method.

            Attempt to find the first valid link item and return it.

            :param toc: The TOC tree list
            :type toc: list

            :return: A found valid link
            :rtype: str
            """
            for toc_item in toc:
                if 'link' in toc_item:
                    return toc_item['link']
                elif 'children' in toc_item:
                    return self._recurse_over_links(toc_item['children'])

        def _recursive_tree_mapping(self, data, trunk, alias):
            """
            Recursive method.

            Insert a branch of directories on its trunk.

            :param data: A set of data (branch, links)
            :type: tuple

            :param trunk: The data structure instance
            :param trunk: dict
            """
            branch, relative_link, absolute_link = data
            parts = branch.split('/', 1)
            if len(parts) == 1:  # branch is a file
                title = self._get_title_from_rst_file(absolute_link)
                trunk[title or '{0}'.format(parts[0]).lower().capitalize()] = relative_link
            else:
                node, others = parts
                if node not in trunk:
                    trunk[node] = collections.OrderedDict()
                    index_path = absolute_link.replace('{0}.rst'.format(branch),
                                                       '{0}/{1}.rst'.format(node, self._master_name))
                    title = self._get_title_from_rst_file(index_path)
                    alias[node] = {
                        '__alias__': title
                        if title != 'Missing' and not self._is_api
                        else ' '.join(node.split('_')).capitalize()
                    }
                self._recursive_tree_mapping((others, relative_link, absolute_link), trunk[node], alias[node])

        def _recursive_tree_analysis(self, lines):
            """
            Recursive method.

            Performs an analysis on links contained in self
            to modify itself according nested index file (that contains another sub-links
            """
            for line in lines:
                stripped = line.strip()

                if not stripped:
                    continue

                if not self.__IS_HIDDEN and ':hidden:' in stripped:
                    self.__IS_HIDDEN = True
                elif self.__IS_HIDDEN and '.. toctree::' in stripped:
                    self.__IS_HIDDEN = False

                if self.__IS_HIDDEN:
                    continue

                might_be_a_link = bool([stripped for typo in self.RST_ALL_TYPOS
                                        if stripped and not stripped.startswith(typo)])
                if not might_be_a_link:
                    continue

                if self._joined_stripped:
                    joined_strip = stripped.replace('/', '.')
                    absolute_link = ProjectHelper.absjoin(self._basepath, '{0}.rst'.format(joined_strip))
                    relative_link = '{0}/{1}.html'.format(self._suffix, joined_strip)
                else:
                    absolute_link = ProjectHelper.absjoin(self._basepath, '{0}.rst'.format(stripped))
                    relative_link = '{0}/{1}.html'.format(self._suffix, stripped)

                if not os.path.isfile(absolute_link):
                    continue

                self.append((stripped, relative_link, absolute_link.replace('\\', '/')))

                if self._joined_stripped:
                    continue

                if stripped.endswith(self._master_name):
                    try:
                        with open(absolute_link, 'r') as hdl:
                            lines = hdl.readlines()
                        if lines:
                            root_index = stripped.replace(self._master_name, '')
                            prepended_lines = []
                            for l in lines:
                                l_stripped = l.strip()
                                if l_stripped:
                                    prepended_lines.append(root_index + l_stripped)
                            self._recursive_tree_analysis(prepended_lines)
                    except errors.SysErrors:
                        pass

        def _recursive_children_analysis(self, data, alias, root_item=None):
            """
            Recursive method.

            Performs Root/Children association on analysed data links
            Therefore preparing well-structured data as expected by the
            Template engine instance

            :param data: A bunch of data
            :type data: dict

            :param root_item: A Root/Parent bunch of data
            :type root_item: dict
            """
            for root, link in data.items():

                is_file = isinstance(link, str)
                is_children = issubclass(link.__class__, dict)
                current_link = 'unknown{0}'.format(Types.TOCList.GLOBAL_ID)

                current_root_item = dict(name=root,
                                         alias="" if is_file else alias[root]['__alias__'],
                                         hash=Types.TOCList.GLOBAL_ID,
                                         children=Types.KeyList(key='hash'))

                Types.TOCList.GLOBAL_ID += 1

                if link and is_file:
                    current_root_item['link'] = current_link = link

                if root_item and current_link not in root_item['children']:
                    root_item['children'].append(current_root_item)
                elif current_link not in self.__items:
                    self.__items.append(current_root_item)

                if link and is_children:
                    self._recursive_children_analysis(link, alias[root], root_item=current_root_item)

        def _recursive_exclude_master_name_items(self, items):
            """
            Recursive method.

            Excludes recursively all items having a link containing the master name string

            :param items: The TOC Items list
            :type items: list
            """
            for idx, item in enumerate(items):
                if self._master_name in item.get('link', ""):
                    del items[idx]
                    del item
                    continue
                children = item.get('children')
                if children:
                    self._recursive_exclude_master_name_items(children)

        def _extract(self):
            """
            Extracts all valid data (paths) from the index.rst file

            :return: Itself to allow chaining pattern on inner (protected) methods
            :rtype: self
            """
            # Make a copy of the Inner list (self)
            lines = self.copy()
            # Clearing the Inner list (self)
            self.clear()
            # Iterate over the copied list and appending valid link(s) to self
            self._recursive_tree_analysis(lines)
            return self

        def clear(self):
            """
            Clears the Inner list (self) and return the removed entries count

            :return: the removed entries count
            :rtype: int
            """
            removed_cnt = len(self)
            del self[:]
            return removed_cnt

        def copy(self, clone=False):
            """
            Return a Copy of the Inner list (self)

            :param clone: If set to True, a real clone of the TOCList is performed
            :type clone: bool

            :return: A Copy of the Inner list
            :rtype: list or Types.TOCList
            """
            copy = self[:]
            if clone:
                self_data = dict(src_dirname=self._basepath,
                                 is_api=self._is_api,
                                 suffix=self._suffix,
                                 maxdepth=self._maxdepth,
                                 master_name=self._master_name,
                                 joined_stripped=self._joined_stripped)
                return Types.TOCList(copy, **self_data)
            return copy

        def build(self):
            """
            Builds the TOC tree by extracting first all valid links from files
            then mapping it to data structure and ordering them recursively from parent (root)
            to children, therefore being well-prepared for templating data

            :return: Itself to allow chaining pattern on public methods
            :rtype: self
            """
            for links in self._extract():
                self._recursive_tree_mapping(links, self.__main_dict, self.__alias)
            self._recursive_children_analysis(self.__main_dict, self.__alias)

            if self._master_name_excluded:
                self._recursive_exclude_master_name_items(self.__items)

            return self

        def pretty_print(self, d=None, indent=4):
            """
            Print the file tree structure with proper indentation.

            :param d: The data structure to be printed
            :param indent: The indentation for the data structure depth

            :return: Itself to allow chaining pattern on public methods
            :rtype: self
            """
            print(json.dumps(d or self.__main_dict, indent=indent))
            print(json.dumps(self.__items, indent=indent))

            return self
