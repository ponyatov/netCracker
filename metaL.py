# generative metaprogramming in Python

import os, sys, re, time
import datetime as dt

## base object (hyper)graph node = Marvin Minsky's Frame
class Object:
    def __init__(self, V):
        ## type/class tag /required for PLY/
        self.type = self.tag()
        ## scalar value: name, number, string..
        self.value = V
        ## associative array: map = env/namespace = grammar attributes
        self.slot = {}
        ## ordered container: vector = stack = queue = AST subtree
        self.nest = []

    ## Python types wrapper
    def box(self, that):
        if isinstance(that, Object): return that
        if isinstance(that, str): return S(that)
        if that is None: return Nil()
        raise TypeError(['box', type(that), that])

    ## @name text tree dump

    ## `print` callback
    def __repr__(self): return self.dump(test=False)

    ## repeatable print for tests
    def test(self): return self.dump(test=True)

    ## full tree dump
    def dump(self, cycle=[], depth=0, prefix='', test=False):
        # head
        ret = self.pad(depth) + self.head(prefix, test)
        # cycle block
        if not depth: cycle = []
        if self in cycle: return ret + ' _/'
        else: cycle.append(self)
        # slot{}s
        for i in self.keys():
            ret += self[i].dump(cycle, depth + 1, f'{i} = ', test)
        # nest[]ed
        for j, k in enumerate(self):
            ret += k.dump(cycle, depth + 1, f'{j}: ', test)
        # subtree
        return ret

    def pad(self, depth, tab='\t'): return '\n' + tab * depth

    ## single `<T:V>` header
    def head(self, prefix='', test=False):
        gid = '' if test else f' @{id(self):x}'
        return f'{prefix}<{self.tag()}:{self.val()}>{gid}'

    ## `<T:`
    def tag(self): return self.__class__.__name__.lower()
    ## `:V>`

    def val(self): return f'{self.value}'

    ## @name operator

    ## `A.keys()`
    def keys(self):
        return sorted(self.slot.keys())

    ## `len(A)`
    def __len__(self):
        return len(self.nest)

    ## `for i in A`
    def __iter__(self):
        return iter(self.nest)

    ## `A[key]`
    def __getitem__(self, key):
        assert isinstance(key, str)
        return self.slot[key]

    ## `A[key] = B`
    def __setitem__(self, key, that):
        assert isinstance(key, str)
        that = self.box(that)
        self.slot[key] = that; return self

    ## `A << B -> A[B.type] = B`
    def __lshift__(self, that):
        that = self.box(that)
        return self.__setitem__(that.tag(), that)

    ## `A >> B -> A[B.value] = B`
    def __rshift__(self, that):
        that = self.box(that)
        return self.__setitem__(that.val(), that)

    ## `A // B -> A.push(B)`
    def __floordiv__(self, that):
        that = self.box(that)
        self.nest.append(that); return self

    def ins(self, idx, that):
        assert isinstance(idx, int)
        that = self.box(that)
        self.nest.insert(idx, that); return self

    def replace(self, idx, that):
        assert isinstance(idx, int)
        that = self.box(that)
        self.nest[idx] = that; return self

    def before(self, where, that):
        assert isinstance(where, Object)
        that = self.box(that)
        ret = []
        for i in self.nest:
            if i == where: ret += [that]
            ret += [i]
        self.nest = ret; return self

    def after(self, where, that):
        assert isinstance(where, Object)
        that = self.box(that)
        ret = []
        for i in self.nest:
            ret += [i]
            if i == where: ret += [that]
        self.nest = ret; return self

    def dropall(self): self.nest = []; return self

class Primitive(Object): pass

class S(Primitive):
    def __init__(self, V=None, end=None, pfx=None, sfx=None):
        super().__init__(V)
        self.end = end
        self.pfx = pfx; self.sfx = sfx

    def gen(self, to, depth=0):
        ret = ''
        if self.pfx is not None:
            if self.pfx: ret += f'{to.tab*depth}{self.pfx}\n'
            else: ret += '\n'
        if self.value is not None:
            ret += f'{to.tab*depth}{self.value}\n'
        for i in self: ret += i.gen(to, depth + 1)
        if self.end is not None:
            ret += f'{to.tab*depth}{self.end}\n'
        if self.sfx is not None:
            if self.sfx: ret += f'{to.tab*depth}{self.sfx}\n'
            else: ret += '\n'
        return ret

class Sec(S):
    def gen(self, to, depth=0):
        ret = ''
        if self:
            if self.pfx is not None:
                if self.pfx: ret += f'{to.tab*depth}{self.pfx}\n'
                else: ret += '\n'
            if self.value is not None:
                ret += f'{to.tab*depth}{to.comment} \\ {self.value}\n'
            for i in self: ret += i.gen(to, depth + 0)
            if self.value is not None:
                ret += f'{to.tab*depth}{to.comment} / {self.value}\n'
            if self.sfx is not None:
                if self.sfx: ret += f'{to.tab*depth}{self.sfx}\n'
                else: ret += '\n'
        return ret


class IO(Object):
    def __init__(self, V):
        super().__init__(V)
        self.path = V

class Dir(IO):
    def sync(self):
        try: os.mkdir(self.path)
        except FileExistsError: pass
        for i in self: i.sync()

    def __floordiv__(self, F):
        assert isinstance(F, IO)
        F.path = f'{self.path}/{F.path}'
        return super().__floordiv__(F)

class File(IO):
    def __init__(self, V, ext='', tab='\t', comment='#'):
        super().__init__(V + ext)
        self.tab = tab; self.comment = comment
        self.top = Sec(); self.bot = Sec()

    def sync(self):
        with open(self.path, 'w') as F:
            F.write(self.top.gen(self))
            for i in self: F.write(i.gen(self))
            F.write(self.bot.gen(self))

class giti(File):
    def __init__(self, V='', ext='.gitignore'):
        super().__init__(V + ext)
        self.bot // '!.gitignore'

class Meta(Object): pass

class Module(Meta):
    def __format__(self, spec):
        if not spec: return f'{self.value}'
        if spec == 'l': return f'{self.value.lower()}'
        raise TypeError(['__format__', spec])

class mkFile(File):
    def __init__(self, V='Makefile', ext='', tab='\t', comment='#'):
        super().__init__(V, ext, tab, comment)

class jsonFile(File):
    def __init__(self, V, ext='.json', tab=' ' * 2, comment='//'):
        super().__init__(V, ext, tab, comment)

class Project(Module):
    def __init__(self, V=None):
        if V is None: V = os.getcwd().split('/')[-1]
        super().__init__(V)
        self.d = Dir(f'{self}')
        self.d_dirs()
        self.vs_code()
        self.f_giti()
        self.f_apt()
        self.f_mk()
        self.r_readme()

    def f_apt(self):
        self.dev = File('apt', '.dev'); self.d // self.dev
        self.dev // 'code meld doxygen'
        self.apt = File('apt', '.txt'); self.d // self.apt
        self.apt // 'git make curl'

    def r_readme(self):
        self.MODULE = self.TITLE = f'{self}'
        self.AUTHOR = 'Dmitry Ponyatov'
        self.EMAIL = 'dponyatov@gmail.com'
        self.YEAR = time.localtime()[0]
        self.LICENSE = 'All rights reserved'
        self.GITHUB = 'https://github.com/ponyatov'
        self.ABOUT = ''
        #
        self.readme = File('README', '.md'); self.d // self.readme
        self.sync_readme()

    def sync_readme(self):
        self.readme.dropall() \
            // f'# ![logo](doc/logo.png) `{self.MODULE}`' \
            // f'## {self.TITLE}' // '' \
            // f'(c) {self.AUTHOR} <<{self.EMAIL}>> {self.YEAR} {self.LICENSE}' // '' \
            // f'github: {self.GITHUB}/{self}' // '' \
            // self.ABOUT

    def f_mk(self):
        self.mk = mkFile(); self.d // self.mk
        self.mk_var()
        self.mk_dir()
        self.mk_tool()
        self.mk_src()
        self.mk_cfg()
        self.mk_all()
        self.mk_rule()
        self.mk_doc()
        self.mk_install()
        self.mk_merge()

    def mk_var(self):
        self.mk.var = Sec('var'); self.mk // self.mk.var
        self.mk.var \
            // '# detect module/project name by current directory' \
            // f'{"MODULE":<7} = $(notdir $(CURDIR))' \
            // '# detect OS name (only Linux/MinGW)' \
            // f'{"OS":<7} = $(shell uname -s)' \
            // '# current date in the `ddmmyy` format' \
            // f'{"NOW":<7} = $(shell date +%d%m%y)' \
            // '# release hash: four hex digits (for snapshots)' \
            // f'{"REL":<7} = $(shell git rev-parse --short=4 HEAD)' \
            // '# current git branch' \
            // f'{"BRANCH":<7} = $(shell git rev-parse --abbrev-ref HEAD)' \
            // '# number of CPU cores (for parallel builds)' \
            // f'{"CORES":<7} = $(shell grep processor /proc/cpuinfo| wc -l)'

    def mk_dir(self):
        self.mk.dir_ = Sec('dir', pfx=''); self.mk // self.mk.dir_
        self.mk.dir_ \
            // '# current (project) directory' \
            // f'{"CWD":<7} = $(CURDIR)' \
            // '# compiled/executable files (target dir)' \
            // f'{"BIN":<7} = $(CWD)/bin' \
            // '# documentation & external manuals download' \
            // f'{"DOC":<7} = $(CWD)/doc' \
            // '# libraries / scripts' \
            // f'{"LIB":<7} = $(CWD)/lib' \
            // '# source code (not for all languages, Rust/C/Java included)' \
            // f'{"SRC":<7} = $(CWD)/src' \
            // '# temporary/flags/generated files' \
            // f'{"TMP":<7} = $(CWD)/tmp'

    def mk_tool(self):
        self.mk.tool = Sec('tool', pfx=''); self.mk // self.mk.tool
        self.mk.tool \
            // '# http/ftp download' \
            // f'{"CURL":<7} = curl -L -o'

    def mk_src(self):
        self.mk.src = Sec('src', pfx=''); self.mk // self.mk.src
        self.mk.src.s = Sec(); self.mk // self.mk.src.s

    def mk_cfg(self):
        self.mk.cfg = Sec('cfg', pfx=''); self.mk // self.mk.cfg

    def mk_all(self):
        self.mk.all_ = Sec('all', pfx=''); self.mk // self.mk.all_
        #
        self.mk.all = S('all:', pfx='.PHONY: all'); self.mk.all_ // self.mk.all
        #
        self.mk.test_ = Sec('test', pfx=''); self.mk.all_ // self.mk.test_
        self.mk.test = S('test:', pfx='.PHONY: test')
        self.mk.test_ // self.mk.test
        #
        self.mk.format_ = Sec(
            'format', pfx=''); self.mk.all_ // self.mk.format_
        self.mk.format = S('tmp/format:',
                           pfx='.PHONY: format\nformat: tmp/format')
        self.mk.format_ // (self.mk.format // 'touch $@')

    def mk_rule(self):
        self.mk.rule = Sec('rule', pfx=''); self.mk // self.mk.rule

    def mk_doc(self):
        self.mk.doc = Sec('doc', pfx=''); self.mk // self.mk.doc
        self.mk.doc // (S('doc:', pfx='.PHONY: doc'))

    def mk_install(self):
        self.mk.install_ = Sec('install', pfx=''); self.mk // self.mk.install_
        #
        self.mk.install = (S('install: $(OS)_install',
                             pfx='.PHONY: install update'))
        self.mk.install_ // (self.mk.install // '$(MAKE) update')
        #
        self.mk.update = (S('update: $(OS)_update'))
        self.mk.install_ // self.mk.update
        #
        self.mk.linux = (S('Linux_install Linux_update:',
                           pfx='\n.PHONY: Linux_install Linux_update'))
        self.mk.install_ // self.mk.linux
        self.mk.install_ \
            // (S('ifneq (,$(shell which apt))', 'endif')
                // 'sudo apt update'
                // 'sudo apt install -u `cat apt.txt apt.dev`')

    def mk_merge(self):
        self.mk.merge_ = Sec('merge', pfx=''); self.mk // self.mk.merge_
        self.mk.merge = Sec(); self.mk.merge_ // self.mk.merge
        self.mk.merge \
            // 'MERGE  = Makefile README.md apt.* .gitignore $(S)' \
            // 'MERGE += .vscode bin doc lib src tmp'
        #
        self.mk.merge_ \
            // (S('dev:', pfx='\n.PHONY: dev') //
                'git push -v' //
                'git checkout $@' //
                'git pull -v' //
                'git checkout ponymuck -- $(MERGE)'
                )
        #
        self.mk.merge_ \
            // (S('ponymuck:', pfx='\n.PHONY: ponymuck')
                // 'git push -v'
                // 'git checkout $@'
                // 'git pull -v'
                )
        #
        self.mk.merge_ \
            // (S('release:', pfx='\n.PHONY: release')
                // 'git tag $(NOW)-$(REL)'
                // 'git push -v --tags'
                // '$(MAKE) ponymuck'
                )
        #
        self.mk.zip_ = \
            (Sec(pfx='')
             // 'ZIP = $(TMP)/$(MODULE)_$(BRANCH)_$(NOW)_$(REL).src.zip')
        self.mk.zip = \
            (S('zip:', pfx='\n.PHONY: zip')
             // 'git archive --format zip --output $(ZIP) HEAD'
             )

        self.mk.zip_ // self.mk.zip
        self.mk.merge_ // self.mk.zip_

    def vs_code(self):
        self.vscode = Dir('.vscode'); self.d // self.vscode
        self.vs_settings()
        self.vs_tasks()
        self.vs_exts()

    def multi(self, key, cmd):
        return (S('{', '},') //
                f'"command": "multiCommand.{key}",'
                // (S('"sequence": [', ']') //
                    '"workbench.action.files.saveAll",'
                    // (S('{"command": "workbench.action.terminal.sendSequence",') //
                        f'"args": {{"text": "\\u000D {cmd} \\u000D"}}}}'
                        )))

    def vs_settings(self):
        self.vscode.settings_ = jsonFile('settings')
        self.vscode // self.vscode.settings_
        self.vscode.settings = S('{', '}')
        self.vscode.settings_ // self.vscode.settings
        #
        self.vscode.multi = S('"multiCommand.commands": [', '],')
        self.vscode.multi \
            // self.multi('f11', 'make test') \
            // self.multi('f12', 'make all')
        #
        self.vscode.files = (Sec('files', pfx=''))
        #
        self.vscode.exclude = Sec() // '"**/docs/**":true,'
        self.vscode.files \
            // (S('"files.exclude": {', '},',
                  pfx='// exclude files from left-side IDE view') //
                self.vscode.exclude)
        #
        self.vscode.watcher = Sec(); self.vscode.files // self.vscode.watcher
        self.vscode.files \
            // (S('"files.watcherExclude": {', '},',
                  pfx='// disable file changes watch (count is limited by OS and slows down refresh)') //
                self.vscode.watcher)
        #
        self.vscode.assoc = Sec(); self.vscode.files // self.vscode.assoc
        self.vscode.files \
            // (S('"files.associations": {', '},',
                  pfx='// associate file types with syntax highlight & editor plugins') //
                self.vscode.assoc)
        #
        self.vscode.editor = (Sec('editor: tunings', pfx='')
                              // '"editor.tabSize": 4,'
                              // '"editor.rulers": [80],'
                              // '"workbench.tree.indent": 32,')
        #
        self.vscode.browser = S(
            '"browser-preview.startUrl": "127.0.0.1:12345/"', pfx='')
        #
        self.vscode.settings \
            // (Sec('multi: hotkey bindings') // self.vscode.multi) \
            // self.vscode.files \
            // self.vscode.editor \
            // self.vscode.browser

    def task(self, group, target):
        return (S('{', '},')
                // f'"label":          "{group}: {target}",'
                // f'"type":           "shell",'
                // f'"command":        "make {target}",'
                // f'"problemMatcher": []')

    def vs_tasks(self):
        self.vscode.tasks_ = jsonFile('tasks')
        #
        self.vscode.tasks = (Sec() //
                             self.task('project', 'install')
                             // self.task('project', 'update')
                             // self.task('git', 'dev')
                             // self.task('git', 'ponymuck')
                             // self.task('metaL', 'meta')
                             )
        #
        self.vscode \
            // (self.vscode.tasks_
                // (S('{', '}') //
                    '"version": "2.0.0",'
                    // (S('"tasks": [', ']') //
                        self.vscode.tasks)))

    def vs_exts(self):
        self.vscode.exts = jsonFile(
            'extensions'); self.vscode // self.vscode.exts
        self.vscode.ext = (Sec() //
                           '"ryuta46.multi-command",'
                           // '"stkb.rewrap",'
                           // '"tabnine.tabnine-vscode",'
                           // '// "auchenberg.vscode-browser-preview",'
                           // '// "ms-azuretools.vscode-docker",')
        self.vscode.exts \
            // (S('{', '}')
                // (S('"recommendations": [', ']') //
                    self.vscode.ext))

    def d_dirs(self):
        self.bin = Dir('bin'); self.d // self.bin
        self.bin // (giti() // '*')
        #
        self.doc = Dir(
            'doc'); self.d // self.doc; self.doc // (giti() // '*.pdf')
        #
        self.lib = Dir('lib'); self.d // self.lib
        self.lib.giti = giti() // '*.a'; self.lib // self.lib.giti
        #
        self.src = Dir('src'); self.d // self.src; self.src // giti()
        #
        self.tmp = Dir('tmp'); self.d // self.tmp; self.tmp // (giti() // '*')

    def f_giti(self):
        self.giti = giti(); self.d // self.giti
        self.giti \
            // '*~' // '*.swp' // '*.log' // '' \
            // '/docs/' // f'/{self}/' // ''

    def sync(self):
        self.sync_readme()
        self.d.sync()

    def __or__(self, mod):
        assert isinstance(mod, Mod)
        return mod.pipe(self)

## Project modifier
class Mod(Module):
    def __init__(self):
        super().__init__('mod')

    def pipe(self, p):
        self.f_giti(p)
        self.f_mk(p)
        self.f_apt(p)
        self.f_src(p)
        self.f_test(p)
        self.vs_code(p)
        return p

    def f_giti(self, p): pass
    def f_mk(self, p): pass
    def f_apt(self, p): pass
    def f_src(self, p): pass
    def f_test(self, p): pass
    def vs_code(self, p): pass

class pyFile(File):
    def __init__(self, V, ext='.py', tab=' ' * 4, comment='#'):
        super().__init__(V, ext, tab, comment)
        self.top // 'import config' // ''

class Python(Mod):
    def pipe(self, p):
        p = super().pipe(p)
        self.f_src(p)
        self.p_reqs(p)
        return p

    def f_apt(self, p):
        super().f_apt(p)
        p.apt // 'python3 python3-venv'

    def p_reqs(self, p):
        p.reqs = File('requirements', '.txt'); p.d // p.reqs

    def f_src(self, p):
        p.config = pyFile('config'); p.d // p.config
        p.config.top = Sec()
        self.p_py(p)

    def p_py(self, p):
        p.py = pyFile(f'{p}'); p.d // p.py
        p.py // self.p_mods()

    def f_test(self, p):
        super().f_test(p)
        p.test = pyFile(f'test_{p}'); p.d // p.test
        p.test \
            // 'import pytest' // f'from {p} import *' // ''
        p.test \
            // 'def test_any(): assert True'

    def f_giti(self, p):
        p.giti // (Sec('py', sfx='')
                   // '/.cache/' // '/__pycache__/' // '*.pyc' // '/pyvenv.cfg'
                   // '/lib/python*/' // '/lib64'
                   // '/share/' // '/include/'
                   )

    PEP8 = '--ignore=E26,E302,E305,E401,E402,E701,E702'

    def vs_code(self, p):
        p.vscode.ext // '"tht13.python",'
        p.vscode.exclude \
            // '"*.pyc":true, "pyvenv.cfg":true,' \
            // '"**/.cache/**":true, "**/__pycache__/**":true,'
        p.vscode.settings.ins(0, (Sec('py', sfx='') //
                                  f'"python.pythonPath"              : "./bin/python3",'
                                  // f'"python.formatting.provider"     : "autopep8",'
                                  // f'"python.formatting.autopep8Path" : "./bin/autopep8",'
                                  // f'"python.formatting.autopep8Args" : ["{Python.PEP8}"],'
                                  ))

    def p_mods(self):
        return (Sec()
                // 'import os, sys, re, time'
                // 'import datetime as dt')

    def f_mk(self, p):
        super().f_mk(p)
        p.mk.src \
            // 'P += config.py' \
            // 'Y += $(MODULE).py test_$(MODULE).py'
        p.mk.src.s // 'S += $(Y)'
        #
        p.mk.all.value += ' $(PY) $(MODULE).py'
        p.mk.all // '$(MAKE) test' // '$^ $@'
        #
        p.mk.test.value += ' test_py'
        p.mk.test_py = (S('test_py: $(PYT) test_$(MODULE).py', pfx='') // '$^')
        p.mk.test_ // p.mk.test_py
        #
        p.mk.format_py = (S('tmp/format_py: $(Y)', pfx=''))
        p.mk.format_ // p.mk.format_py
        p.mk.format.value += ' tmp/format_py'
        p.mk.format_py // f'$(PEP) {Python.PEP8} --in-place $?'
        #
        p.mk.tool \
            // f'{"PY":<7} = $(BIN)/python3' \
            // f'{"PIP":<7} = $(BIN)/pip3' \
            // f'{"PYT":<7} = $(BIN)/pytest' \
            // f'{"PEP":<7} = $(BIN)/autopep8'
        p.mk.update \
            // '$(PIP) install -U pytest autopep8' \
            // '$(PIP) install -U -r requirements.txt'
        p.mk.install.ins(0, '$(MAKE) $(PIP)')
        p.mk.install_ \
            // (S('$(PY) $(PIP) $(PYT) $(PEP):', pfx='')
                // 'python3 -m venv .')
        #
        p.mk.merge // 'MERGE += requirements.txt $(Y)'


class rsFile(File):
    def __init__(self, V, ext='.rs', tab=' ' * 4, comment='//'):
        super().__init__(V, ext, tab, comment)

class tomlFile(File):
    def __init__(self, V, ext='.toml', tab=' ' * 4, comment='#'):
        super().__init__(V, ext, tab, comment)

class Rust(Mod):
    def pipe(self, p):
        p = super().pipe(p)
        return p

    def f_giti(self, p):
        super().f_giti(p)
        p.giti // '/target/' // '/Cargo.lock' // ''

    def f_mk(self, p):
        super().f_mk(p)
        p.mk.dir_ \
            // '# Rust toolchain' \
            // f'{"CAR":<7} = $(HOME)/.cargo/bin'
        p.mk.tool \
            // f'{"RUSTUP":<7} = $(CAR)/rustup' \
            // f'{"CARGO":<7} = $(CAR)/cargo' \
            // f'{"RUSTC":<7} = $(CAR)/rustc'
        #
        p.mk.src // 'R += $(shell find src -type f -regex ".+.rs$$")'
        p.mk.src.s // 'S += $(R)'
        p.mk.all.value = 'all: Cargo.toml $(R)'
        p.mk.all.dropall() \
            // '$(CARGO) test && $(CARGO) fmt' \
            // 'RUST_LOG=trace $(CARGO) run'
        #
        p.mk.test.value += ' test_rs'
        p.mk.test_rs = \
            (S('test_rs: Cargo $(R)', pfx='')
                // '$(CARGO) test')
        p.mk.test_ // p.mk.test_rs
        #
        p.mk.format_rs = (S('tmp/format_rs: $(Y)', pfx=''))
        p.mk.format_ // p.mk.format_rs
        p.mk.format.value += ' tmp/format_rs'
        p.mk.format_rs // f'$(CARGO) fmt'
        #
        p.mk.install.ins(-1, '$(MAKE) $(RUSTUP)')
        p.mk.install_ \
            // (S('$(RUSTUP):', pfx='\nrust: $(RUSTUP)')
                // 'curl --proto \'=https\' --tlsv1.2 -sSf https://sh.rustup.rs | sh')
        p.mk.update \
            // '$(RUSTUP) update' \
            // '$(CARGO) update'
        #
        p.mk.merge // 'MERGE += Cargo.toml $(R)'

    def f_src(self, p):
        super().f_src(p)
        self.f_cargo(p)
        self.f_main(p)
        self.f_test(p)

    def f_main(self, p):
        p.rs = rsFile('main'); p.src // p.rs
        #
        p.rs.mod = Sec('mod'); p.rs // (p.rs.mod // 'mod test;')
        #
        p.rs.extern = Sec('extern', pfx=''); p.rs // p.rs.extern
        p.rs.extern \
            // 'extern crate tracing;'
        #
        p.rs.use = Sec('use', pfx=''); p.rs // p.rs.use
        p.rs.use \
            // 'use tracing::{info, instrument};'
        #
        p.rs.main = S('fn main() {', '}', pfx='\n#[instrument]')
        p.rs // p.rs.main
        #
        p.rs.main.init = Sec('init')
        #
        p.rs.main \
            // 'tracing_subscriber::fmt::init();' \
            // 'info!("start");'
        p.rs.main \
            // p.rs.main.init
        p.rs.main \
            // 'info!("stop");'

    def f_test(self, p):
        p.rs.test = rsFile('test'); p.src // p.rs.test
        p.rs.test \
            // '#[cfg(test)]'
        p.rs.test \
            // '#[test]' \
            // (S('fn any() {', '}') // 'assert!(true);')

    def f_cargo(self, p):
        p.cargo = tomlFile('Cargo'); p.d // p.cargo
        p.cargo.package = Sec(pfx='[package]'); p.cargo // p.cargo.package
        p.cargo.package \
            // f'name    = "{p:l}"' \
            // f'version = "0.0.1"' \
            // f'authors = ["{p.AUTHOR} <{p.EMAIL}>"]'
        p.cargo.deps = Sec(pfx='\n[dependencies]'); p.cargo // p.cargo.deps
        p.cargo.tracing = \
            (Sec('telemetry', pfx='') //
             '# logging mostly used in any program runs in batch or manual'
             // '# log = "0.4"'
             // '# structured logging'
             // 'tracing = "0.1"'
             // 'tracing-subscriber = "0.2"')
        p.cargo.deps \
            // '# program initialization at startup and exit' \
            // 'static_init = "1.0"' \
            // '# FFI interface with standard libc required for any system tool' \
            // 'libc = "0.2"' \
            // p.cargo.tracing \
            // ''


class metaL(Python):
    def pipe(self, p):
        p = super().pipe(p)
        self.p_metal(p)
        return p

    def f_giti(self, p):
        pass

    def p_metal(self, p):
        p.metal = pyFile('metaL'); p.d // p.metal
        p.metal.top.dropall()
        p.metal // self.p_mods()

    def vs_code(self, p):
        p.vscode.exclude // f'"**/{p}/**":true,'
        super().vs_code(p)
        p.vscode.multi.replace(0, p.multi('f11', 'make meta'))

    def f_mk(self, p):
        # super().f_mk(p)
        p.mk.src // 'Y += metaL.py test_metaL.py'
        # p.mk.test_py.value += ' test_metaL.py'
        if hasattr(p, 'py'):
            p.mk.all_ \
                // (S('meta: $(PY) metaL.py', pfx='\n.PHONY: meta')
                    // '$(MAKE) test_py tmp/format_py' // '$^ $@')
        else:
            p.mk.tool \
                // f'{"PY":<7} = python3' \
                // f'{"PIP":<7} = pip3' \
                // f'{"PEP":<7} = $(HOME)/.local/bin/autopep8'
            p.mk.src.s \
                // 'S += $(Y)'
            p.mk.all_ \
                // (S('meta: metaL.py', pfx='\n.PHONY: meta')
                    // '$(PY) $<'
                    // f'$(PEP) {Python.PEP8} --in-place $<')
            p.mk.update \
                // '$(PIP) install --user -U autopep8'

class javaFile(File):
    def __init__(self, V, ext='.java', tab=' ' * 2, comment='//'):
        super().__init__(V, ext, tab, comment)

class Java(Mod):

    def __init__(self, package):
        super().__init__()
        self.package = package

    def pipe(self, p):
        p = super().pipe(p)
        p.package = self.package
        return p

    def vs_code(self, p):
        super().vs_code(p)
        p.vscode.ext // '"redhat.java",'

    def f_apt(self, p):
        super().f_apt(p)
        p.dev // 'default-jdk-headless' // 'libantlr-dev'

    def mk_jar(self, p):
        p.lib.giti // '*.jar'
        p.mk.dir_ // S(f'{"CP":<7} = bin',
                       pfx='# project local CLASS_PATH')
        #
        p.mk.jar = Sec('jar', pfx='')
        p.mk.after(p.mk.dir_, p.mk.jar)
        #
        # // f'{"GJF_VER":<13}  = 1.11.0'
        p.mk.jar \
            // (Sec()
                // f'{"GJF_VER":<13}  = 1.7'
                // f'{"GJF_JAR":<13}  = google-java-format-$(GJF_VER).jar'
                // f'{"GJF":<13}  = lib/$(GJF_JAR)')
        p.mk.jar \
            // (Sec(pfx='')
                // f'{"JUNIT_VER":<13}  = 4.13.2'
                // f'{"JUNIT_JAR":<13}  = junit-$(JUNIT_VER).jar'
                // f'{"JUNIT":<13}  = lib/$(JUNIT_JAR)'
                // f'{"CP":<13} += $(JUNIT)')
        p.mk.jar \
            // (Sec(pfx='')
                // f'{"HAMCREST_VER":<13}  = 2.2'
                // f'{"HAMCREST_JAR":<13}  = hamcrest-$(HAMCREST_VER).jar'
                // f'{"HAMCREST":<13}  = lib/$(HAMCREST_JAR)'
                // f'{"CP":<13} += $(HAMCREST)')
        #
        p.mk.cfg \
            // (Sec()
                // f'{"JPATH":<7} = -cp $(shell echo $(CP) | sed "s/ /:/g")'
                // f'{"JFLAGS":<7} = -d $(BIN) $(JPATH)')

    def f_mk(self, p):
        super().f_mk(p)
        p.mk.var \
            // (S(f'{"PACKAGE":<7} = {self.package}',
                  pfx='# Java project package'))
        p.mk.tool \
            // f'{"JAVA":<7} = $(JAVA_HOME)/bin/java' \
            // f'{"JAVAC":<7} = $(JAVA_HOME)/bin/javac'
        #
        p.mk.src // 'J += $(shell find src -type f -regex ".+.java$$")'
        p.mk.src.s // 'S += $(J)'
        p.mk.cfg // f'{"CLASS":<7} = $(shell echo $(J) | sed "s|\\.java|.class|g" | sed "s|src/|bin/|g")'
        #
        p.mk.all.value += ' test format'
        #
        p.mk.test.value += ' $(CLASS)'
        p.mk.tests = Sec()
        p.mk.test_.before(p.mk.test, p.mk.tests)
        p.mk.test \
            // (S('$(JAVA) $(JPATH) \\')
                // 'org.junit.runner.JUnitCore $(TESTS)')
        #
        p.mk.rule // (S('$(CLASS): $(J)')
                      // '$(JAVAC) $(JFLAGS) $^'
                      // '$(MAKE) format')
        #
        p.mk.format.value += ' $(J)'
        p.mk.format.ins(0,
                        '$(JAVA) $(JPATH) -jar $(GJF) --replace $?')
        #
        self.mk_jar(p)
        self.mk_install(p)

    def mk_test(self, p):
        p.mk.test \
            // (S('$(JAVA) $(JPATH) \\')
                // (S('org.junit.runner.JUnitCore $(TESTS)')))

    def mk_install(self, p):
        #
        p.mk.install.ins(0, '$(MAKE) gjf junit')
        #
        # // '$(CURL) $@ https://github.com/google/google-java-format/releases/download/v$(GJF_VER)/google-java-format-$(GJF_VER)-all-deps.jar'
        p.mk.install_ \
            // (S('$(GJF):', pfx='\ngjf: $(GJF)')
                // '$(CURL) $@ https://github.com/google/google-java-format/releases/download/google-java-format-$(GJF_VER)/google-java-format-$(GJF_VER)-all-deps.jar'
                )
        #
        p.mk.install_ \
            // (S('$(JUNIT):', pfx='\njunit: $(JUNIT) $(HAMCREST)')
                // '$(CURL) $@ https://search.maven.org/remotecontent?filepath=junit/junit/$(JUNIT_VER)/$(JUNIT_JAR)'
                )
        #
        p.mk.install_ \
            // (S('$(HAMCREST):', pfx='\nhamcrest: $(HAMCREST)')
                // '$(CURL) $@ https://search.maven.org/remotecontent?filepath=org/hamcrest/hamcrest/$(HAMCREST_VER)/$(HAMCREST_JAR)'
                )

    def f_src(self, p):
        super().f_src(p)
        for i in self.package.split('.'):
            curr = p.src
            p.src = Dir(i)
            curr // p.src
        p.src // giti()

    def f_test(self, p):
        super().f_test(p)
        p.test = Dir('test'); p.src // p.test; p.test // giti()


# from metaL import *
prj = Project() | metaL() | Java('com.nc.edu.ta.ponyatov.pr2')
prj.TITLE = 'Java/TA: personal task tracker'

prj.src.task = javaFile('Task'); prj.src // prj.src.task
prj.src.task // f'package {prj.package};' // ''

prj.mk.tests \
    // 'TESTS += $(PACKAGE).test.MyTest' \
    // 'TESTS += $(PACKAGE).test.PartialTest' \
    // ''
prj.test.task = javaFile('MyTest'); prj.test // prj.test.task
prj.test.task \
    // f'package {prj.package}.test;' // '' \
    // f'import {prj.package}.*;' // '' \
    // 'import org.junit.*;' // '' \
    // ''

prj.mk.zip // 'zip $(ZIP) lib/*.jar'

prj.sync()
