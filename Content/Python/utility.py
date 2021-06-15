import os
import sys
import time
import subprocess
import ctypes
import shutil
import glob
import fnmatch

# TODO:使用logging替代该功能
######################
######################
#       Log          #
######################
######################

LOG_LEVEL = None
LOG_LEVEL_NORMAL = 0
LOG_LEVEL_INFO = 1
LOG_LEVEL_WARNING = 2
LOG_LEVEL_ERROR = 3
LOG_LEVEL_SUCCESS = 4
LOG_LEVEL_NONE = 99
LOG_INDENT = 0


def color_message(message, color_code, bold=False):
    if is_win():
        os.system('')
    result = '\033[{}m{}\033[0m'.format(color_code, message)
    if bold:
        result = '\033[1m' + result
    return result


def log(message, level=LOG_LEVEL_NORMAL, noident=False, bold=False):
    global LOG_INDENT, LOG_LEVEL

    if LOG_LEVEL is None:
        LOG_LEVEL = int(get_env('SCRIPT_LOG_LEVEL', -1))

    if level >= LOG_LEVEL:
        if level == LOG_LEVEL_INFO:
            message = color_message(message, 34, bold)

        if level == LOG_LEVEL_WARNING:
            message = color_message('warning: {}'.format(message), 33, bold)

        if level == LOG_LEVEL_ERROR:
            message = color_message('error: {}'.format(message), 31, bold)

        if level == LOG_LEVEL_SUCCESS:
            message = color_message('success: {}'.format(message), 32, bold)

        if not is_win():
            message = message.replace('=>', '➜').replace('<=', '✔')

        message += '\n'

        pipe = sys.stdout if level == LOG_LEVEL_NORMAL else sys.stderr

        pipe.write(('' if noident else ('  ' * LOG_INDENT)) + message)


def info(message, bold=False):
    log(message, LOG_LEVEL_INFO, False, bold)


def warning(message, bold=False):
    log(message, LOG_LEVEL_WARNING, False, bold)


def error(message, bold=False):
    set_env('__SCRIPT_ERROR', 1)
    set_env('__SCRIPT_LAST_ERROR_MESSAGE', message)
    log(message, LOG_LEVEL_ERROR, False, bold)

######################
######################
#       操作系统      #
######################
######################


def is_win():
    return sys.platform.lower().startswith('win')


######################
######################
#       环境变量      #
######################
######################


def get_env(key, default=None):
    # 从环境变量中获取指定键，如果没有则使用default指定的值
    if key in os.environ:
        value = os.environ[key]
        if value == 'None' or len(value) == 0:
            value = default
        return value
    else:
        return default


def set_env(key, value='None'):
    # 设置环境变量中指定键，如果没有传值则设置为None
    if value is not None:
        os.environ[key] = str(value)
    return value


def get_val(dict, key, default=None):
    if key in dict:
        return dict[key]
    else:
        return default


def is_ci_mode():
    return get_env('__SCRIPT_CI_MODE') is not None


# https://blog.csdn.net/doots/article/details/86705182
SET_ENV = r'''
@echo off
set %{key}%={value}

if {user}==sys (
	setx /M {key} "{value}"
) else (
	setx {key} "{value}"
)
'''

ADD_ENV = r'''
@echo off

if {user}==sys (
	set regPath= HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session" "Manager\Environment
) else (
	set regPath= HKEY_CURRENT_USER\Environment
)

set key={key}
set value={value}
:: 判断是否存在该路径
reg query %regPath% /v %key% 1>nul 2>nul
if %ERRORLEVEL%==0 (
	:: 取值
	For /f "tokens=3* delims= " %%i in ('Reg Query %regPath% /v %key% ') do (
		if "%%j"=="" (Set oldValue=%%i) else (Set oldValue=%%i %%j)
	)
) else Set oldValue=""

:: 备份注册表
@REM reg export %regPath% %~dp0%~n0.reg
:: 写入环境变量
if "%oldValue%"=="" (
	reg add %regPath% /v %key% /t REG_EXPAND_SZ /d "%value%" /f
) else (
    if {override}==True (
	    reg add %regPath% /v %key% /t REG_EXPAND_SZ /d "%value%" /f
    ) else (
	    reg add %regPath% /v %key% /t REG_EXPAND_SZ /d "%oldValue%;%value%" /f
    )
)
'''


def set_env_win(key, value, override=False):
    if is_win():
        if value[-1] == '\\':
            value = value[:-1] + '/'
        # 运行设置环境变量命令
        bat_cmd = ADD_ENV.format(
            user='me', key=key, value=value, override=override)
        # info('=> run cmd : \n {}'.format(bat_cmd))
        tmp_bat_name = 'SET_ENV.bat'
        f = open(tmp_bat_name, 'w+')
        f.write(bat_cmd)
        f.close()
        execute('./{}'.format(tmp_bat_name), verbose=True)
        os.remove(tmp_bat_name)
        if override:
            info('=> Set system environment {0}={1} finished.'.format(
                key, value))
        else:
            info('=> Append {1} to system environment key {0}.'.format(
                key, value))

########################
########################
#       文件系统        #
########################
########################


def search_pattern(pattern, validator=None):
    if is_win():
        volumes = get_all_volumes()
        for volume in volumes:
            seach_path = os.path.join(volume, pattern)
            info('=> Searching at {}'.format(seach_path), False)
            result = glob.glob(seach_path, recursive=True)
            if len(result) > 0:
                for find_path in result:
                    if validator is None or validator(find_path):
                        return find_path


def copy_files(target_path, src_file_list):
    for src_file in src_file_list:
        if os.path.exists(src_file):
            src_basename = os.path.basename(src_file)
            deploy_file_path = os.path.join(target_path, src_basename)
            deploy_dir = os.path.dirname(deploy_file_path)
            if not os.path.exists(deploy_dir):
                os.makedirs(deploy_dir)
                info('Makedirs => {}'.format(deploy_dir))
            if os.path.isfile(deploy_file_path):
                os.remove(deploy_file_path)
                info('Removed => {}'.format(deploy_file_path))

            shutil.copy(src_file, deploy_file_path)
            info('Copy file from {} to => {}'.format(src_file, deploy_file_path))


def read_file(file, decode='utf-8'):
    if os.path.isfile(file):
        content = ''
        with open(file, 'rb') as fo:
            content = fo.read()
        fo.close()
        content = content.decode(decode)
        return content
    else:
        error('{} is not found or is not a file'.format(file))


def get_all_volumes():
    if is_win():
        lp_buffer = ctypes.create_string_buffer(78)
        ctypes.windll.kernel32.GetLogicalDriveStringsA(
            ctypes.sizeof(lp_buffer), lp_buffer)
        all_volumes = lp_buffer.raw.split(b'\x00')
        legal_volumes = []
        for vol in all_volumes:
            s = str(vol, encoding='utf-8')
            if os.path.isdir(s):
                legal_volumes.append(s)
        return legal_volumes

def get_files(work_dir, include_patterns=None, ignore_patterns=None, follow_links=False, recursive=True, apply_ignore_when_conflick=True):
    # ** 
    # 根据包含规则和忽略规则，获得指定目录下的文件列表
    #
    # @work_dir (str)
    #   根目录
    # @include_patterns (list(str))
    #   包含路径的规则，可以与忽略规则同时生效
    #   NOTE:这里的patterns用的是UNIX通配符，而非语言正则表达式
    # @ignore_patterns (list(str))
    #   忽略路径的规则，满足该规则并且不与包含路径冲突则文件被忽略
    #   NOTE:这里的patterns用的是UNIX通配符，而非语言正则表达式
    # @follow_links (bool)
    #   遍历是否包含文件链接
    # @recursive (bool)
    #   是否递归
    # @apply_ignore_when_conflick (bool)
    #   包含规则与忽略规则冲突时，优先遵守忽略规则
    # **
    if os.path.isfile(work_dir):
        result = [work_dir]
    else:
        result = []
        walk_result = os.walk(work_dir, followlinks=follow_links)
        if not recursive:
            try:
                walk_result = [next(walk_result)]
            except:
                walk_result = None
        if walk_result is not None:
            for dirpath, _, filenames in walk_result:
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    valid = True
                    if ignore_patterns is not None:
                        for ignore_pattern in ignore_patterns:
                            match_result = fnmatch.fnmatch(full_path, ignore_pattern)
                            valid = valid and not match_result
                            if not valid:
                                break
                    if include_patterns is not None:
                        for include_pattern in include_patterns:
                            match_result = fnmatch.fnmatch(full_path, include_pattern)
                            if apply_ignore_when_conflick:
                                valid = match_result and valid
                            else:
                                valid = match_result or valid
                            if valid:
                                break
                    if valid:
                        result.append(full_path)
    return sorted(result)

######################
######################
#   执行脚本or模块    #
######################
######################


class ExecuteResult:
    def __init__(self):
        self.code = 0
        self.out = None
        self.error = None
        self.exception = None


ext_2_shell = {
    # NOTE:windows调用sh
    '.sh': 'git-bash',
    '.py': 'python'
}


def format_args(args):
    if type(args) is list:
        return ' '.join(args)
    elif type(args) is str:
        return args
    else:
        info('Unsupported args type : {}'.format(type(args)))
        return ' '


def execute_straight(cmd, args, verbose=True, ignore_error=False, use_direct_stdout=False, exit_at_once=False, env=None, shell=True):
    args = format_args(args)
    cmd_line = '{0} {1}'.format(cmd, args)

    if verbose:
        global LOG_INDENT
        LOG_INDENT += 1
        info('=> Shell: {}'.format(cmd_line), True)

    set_env('__SCRIPT_ERROR', None)
    start_time = time.time()

    pipes = subprocess.Popen(cmd_line, stdout=sys.stdout if use_direct_stdout else subprocess.PIPE,
                             stderr=subprocess.PIPE, env=env, shell=shell)
    result = ExecuteResult()
    if exit_at_once:
        result.code = 0
    else:
        result.out, result.error = pipes.communicate()
        result.out = "" if result.out is None else result.out.strip()
        result.error = "" if result.error is None else result.error.strip()
        result.code = pipes.returncode

    if verbose:
        info('<= Finished: {0} {1:.2f} seconds'.format(
            os.path.basename(cmd), time.time() - start_time), True)

    if not ignore_error and result.code != 0:
        if verbose:
            error('Command failed: {} \n code: {} \n message: {}'.format(
                cmd_line, result.code, result.error if result.error != '' else result.out), True)
        sys.exit(-1)
    if verbose:
        LOG_INDENT -= 1
    return result


def execute(script, args, work_dir=None, verbose=True, ignore_error=False, use_direct_stdout=False, exit_at_once=False, env=None, shell=True):
    args = format_args(args)
    previous_cwd = os.getcwd()
    if work_dir is not None:
        # should be restore
        os.chdir(os.path.realpath(work_dir))

    ext = os.path.splitext(script)
    result = None
    if not ext[1] in ext_2_shell:
        result = execute_straight(
            script, args, verbose, ignore_error, use_direct_stdout, exit_at_once, env, shell)
    else:
        shell = ext_2_shell[ext[1]]
        script = '{} {}'.format(shell, script)
        result = execute_straight(
            script, args, verbose,  ignore_error, use_direct_stdout, exit_at_once, env, shell)

    os.chdir(previous_cwd)
    return result


def execute_module(module, *module_parameters):
    global LOG_INDENT
    LOG_INDENT += 1

    module_name = module.__name__
    info('=> Module: {}'.format(module_name), True)
    set_env('__SCRIPT_ERROR', None)
    start_time = time.time()
    result = module.main(*module_parameters)
    info('<= Finished: {0} {1:.2f} seconds '.format(
        module_name, time.time() - start_time), True)

    LOG_INDENT -= 1
    return result
