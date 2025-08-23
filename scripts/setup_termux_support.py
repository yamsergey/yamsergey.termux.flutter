#!/usr/bin/env python3
"""
Direct Termux support setup for Flutter engine.
This script applies all necessary changes without relying on git patches.
"""

import os
import sys
import re
from pathlib import Path

def create_termux_build_gn(engine_src_path):
    """Create the termux BUILD.gn file with Android log library support."""
    termux_config_dir = engine_src_path / "build" / "config" / "termux"
    termux_config_dir.mkdir(parents=True, exist_ok=True)
    
    build_gn_content = '''import("//build/config/termux/termux.gni")
import("//build/config/sysroot.gni")
import("//build/config/profiler.gni")

config("compiler") {
  if (current_toolchain == "//build/toolchain/termux:${current_cpu}") {
    cflags = [
      "-fno-strict-aliasing",
      "-fstack-protector",
      "--param=ssp-buffer-size=8",
      "-fPIC",
      "-pipe",
      "-fcolor-diagnostics",
      "-ffunction-sections",
      "-funwind-tables",
      "-fno-short-enums",
      "-nostdinc++",
    ]
    cflags_cc = ["-fvisibility-inlines-hidden"]
    cflags_objcc = ["-fvisibility-inlines-hidden"]
    ldflags = [
      "-Wl,--fatal-warnings",
      "-fPIC",
      "-Wl,-z,noexecstack",
      "-Wl,-z,now",
      "-Wl,-z,relro",
      "-Wl,--undefined-version",
      "-Wl,--no-undefined",
      "-Wl,--exclude-libs,ALL",
      "-Wl,--icf=all",
      "-Wl,-z,max-page-size=65536",
    ]
    defines = [
      "__TERMUX__",
      "HAVE_SYS_UIO_H"
    ]
    if (!using_sanitizer) {
      ldflags += [ "-Wl,-z,defs" ]
    }
    if (enable_profiling && !is_debug) {
      defines += [ "ENABLE_PROFILING" ]
      cflags += [
        "-fno-omit-frame-pointer",
        "-mno-omit-leaf-frame-pointer",
        "-g",
      ]

      if (enable_full_stack_frames_for_profiling) {
        cflags += [
          "-fno-inline",
          "-fno-optimize-sibling-calls",
        ]
      }
      ldflags += [ "-rdynamic" ]
    }
    if (using_sanitizer) {
      cflags += [
        "-fno-omit-frame-pointer",
        "-gline-tables-only",
      ]
    }
    if (is_asan) {
      cflags += [ "-fsanitize=address" ]
      ldflags += [ "-fsanitize=address" ]
    }
    if (is_lsan) {
      cflags += [ "-fsanitize=leak" ]
      ldflags += [ "-fsanitize=leak" ]
    }
    if (is_tsan) {
      cflags += [ "-fsanitize=thread" ]
      ldflags += [ "-fsanitize=thread" ]
    }
    if (is_msan) {
      cflags += [ "-fsanitize=memory" ]
      ldflags += [ "-fsanitize=memory" ]
    }
    if (is_ubsan) {
      cflags += [ "-fsanitize=undefined" ]
      ldflags += [ "-fsanitize=undefined" ]
    }
    if (current_cpu == "x64") {
      cflags += [
        "-m64",
        "-march=x86-64",
      ]
      ldflags += [ "-m64" ]
    } else if (current_cpu == "x86") {
      cflags += [ "-m32" ]
      ldflags += [ "-m32" ]
      if (is_clang) {
        cflags += [
          "-mstack-alignment=16",
          "-mstackrealign",
        ]
      }
    } else if (current_cpu == "arm") {
      cflags += [
        "-march=$arm_arch",
        "-mfloat-abi=$arm_float_abi",
      ]
      if (arm_tune != "") {
        cflags += [ "-mtune=$arm_tune" ]
      }
      if (arm_use_thumb) {
        cflags += [ "-mthumb" ]
      }
    }
    if (current_cpu == "arm") {
      cflags += [ "--target=arm-linux-androideabi${termux_api_level}" ]
      ldflags += [ "--target=arm-linux-androideabi${termux_api_level}" ]
    } else if (current_cpu == "arm64") {
      cflags += [ "--target=aarch64-linux-android${termux_api_level}" ]
      ldflags += [ "--target=aarch64-linux-android${termux_api_level}" ]
    } else if (current_cpu == "x86") {
      cflags += [ "--target=i686-linux-androideabi${termux_api_level}" ]
      ldflags += [ "--target=i686-linux-androideabi${termux_api_level}" ]
    } else if (current_cpu == "x64") {
      cflags += [ "--target=x86_64-linux-androideabi${termux_api_level}" ]
      ldflags += [ "--target=x86_64-linux-androideabi${termux_api_level}" ]
    }
    asmflags = cflags
  } else {
    configs = ["//build/config/compiler:compiler"]
  }
}

config("runtime_library") {
  if (current_toolchain == "//build/toolchain/termux:${current_cpu}") {
    cflags_cc = ["-nostdinc++"]
    cflags_objcc = [ "-nostdinc++" ]
    defines = [
      "__compiler_offsetof=__builtin_offsetof",
      "nan=__builtin_nan"
    ]
    ldflags = [
      "-stdlib=libstdc++",
      "-Wl,--warn-shared-textrel"
    ]
    lib_dirs = [ "$custom_toolchain/lib/clang/19/lib/linux/" ]
    include_dirs = [
      "//flutter/third_party/libcxx/include",
      "//flutter/third_party/libcxxabi/include",
    ]
  } else {
    configs = ["//build/config/compiler:runtime_library"]
  }
}

config("executable_ldconfig") {
  if (current_toolchain == "//build/toolchain/termux:${current_cpu}") {
    ldflags = [
      "-Bdynamic",
      "-Wl,-z,nocopyreloc",
    ]
  } else {
    configs = ["//build/config/gcc:executable_ldconfig"]
  }
}

# TODO: limit to linux:sdk
config("sdk") {
  cflags = []
  ldflags = [ "-Wl,-rpath=/data/data/com.termux/files/usr/lib" ]
  libs = [ "log" ]  # Add Android log library for __android_log_write
  lib_dirs = [ "$custom_toolchain/lib/clang/19/lib/linux/" ]
  if (defined(target_sysroot) && target_sysroot != "") {
    cflags += [ "--sysroot=" + target_sysroot ]
    ldflags += [ "--sysroot=" + target_sysroot ]
  }
  if (defined(custom_sysroot) && custom_sysroot != "") {
    cflags += [ "-idirafter$custom_sysroot/usr/include" ]
    lib_dirs += [ "$custom_sysroot/usr/lib" ]
  }
}
'''
    
    build_gn_path = termux_config_dir / "BUILD.gn"
    with open(build_gn_path, 'w') as f:
        f.write(build_gn_content)
    
    print(f"✓ Created {build_gn_path}")
    return build_gn_path

def create_termux_gni(engine_src_path):
    """Create the termux.gni file."""
    termux_config_dir = engine_src_path / "build" / "config" / "termux"
    termux_config_dir.mkdir(parents=True, exist_ok=True)
    
    termux_gni_content = '''declare_args() {
  termux_api_level = 26

  is_termux = false
  is_termux_host = false
}
'''
    
    termux_gni_path = termux_config_dir / "termux.gni"
    with open(termux_gni_path, 'w') as f:
        f.write(termux_gni_content)
    
    print(f"✓ Created {termux_gni_path}")
    return termux_gni_path

def create_termux_toolchain(engine_src_path):
    """Create the termux toolchain BUILD.gn file."""
    termux_toolchain_dir = engine_src_path / "build" / "toolchain" / "termux"
    termux_toolchain_dir.mkdir(parents=True, exist_ok=True)
    
    toolchain_content = '''import("//build/toolchain/gcc_toolchain.gni")
import("//build/config/android/config.gni")
import("//build/config/termux/termux.gni")
import("//build/toolchain/custom/custom.gni")

template("termux_toolchain") {
  gcc_toolchain(target_name) {
    assert(defined(custom_toolchain) && custom_toolchain != "")

    is_clang = true
    toolchain_os = "linux"
    toolchain_cpu = invoker.toolchain_cpu

    prefix = "$custom_toolchain/bin"
    cc = prefix + "/clang"
    cxx = prefix + "/clang++"
    asm = prefix + "/clang"
    ar = prefix + "/llvm-ar"
    ld = prefix + "/clang++"
    readelf = prefix + "/llvm-readelf"
    nm = prefix + "/llvm-nm"
    strip = prefix + "/llvm-strip"
  }
}

termux_toolchain("arm64"){
  toolchain_cpu = "arm64"
}

termux_toolchain("arm"){
  toolchain_cpu = "arm"
}

termux_toolchain("x64"){
  toolchain_cpu = "x64"
}

termux_toolchain("x86"){
  toolchain_cpu = "x86"
}
'''
    
    toolchain_path = termux_toolchain_dir / "BUILD.gn"
    with open(toolchain_path, 'w') as f:
        f.write(toolchain_content)
    
    print(f"✓ Created {toolchain_path}")
    return toolchain_path

def modify_buildconfig_gn(engine_src_path):
    """Modify BUILDCONFIG.gn to use termux configurations."""
    buildconfig_path = engine_src_path / "build" / "config" / "BUILDCONFIG.gn"
    
    with open(buildconfig_path, 'r') as f:
        content = f.read()
    
    # Replace compiler configurations in _native_compiler_configs
    content = content.replace(
        '"//build/config/compiler:compiler",',
        '"//build/config/termux:compiler",'
    )
    content = content.replace(
        '"//build/config/compiler:runtime_library",',
        '"//build/config/termux:runtime_library",'
    )
    
    # Add termux import after the existing imports section
    if 'import("//build/config/termux/termux.gni")' not in content:
        # Find the right place to add the import - before the is_linux check
        pattern = r'(if \(is_linux\) \{)'
        replacement = 'import("//build/config/termux/termux.gni")\n\nif (is_termux) {\n  _native_compiler_configs += [ "//build/config/termux:sdk" ]\n} else if (is_linux) {'
        content = re.sub(pattern, replacement, content)
    
    # Replace executable ldconfig
    content = content.replace(
        '"//build/config/gcc:executable_ldconfig"',
        '"//build/config/termux:executable_ldconfig"'
    )
    
    # Add termux toolchain selection
    pattern = r'(if \(custom_toolchain != ""\) \{)'
    replacement = '''if (is_termux) {
  host_toolchain = "//build/toolchain/linux:clang_$host_cpu"
  set_default_toolchain("//build/toolchain/termux:$current_cpu")
} else if (custom_toolchain != "") {'''
    content = re.sub(pattern, replacement, content)
    
    # Add termux host toolchain support
    pattern = r'(} else \{\s*assert\(false, "Toolchain not set because of unknown platform\."\)\s*})'
    replacement = '''} else {
  assert(false, "Toolchain not set because of unknown platform.")
}
if (is_termux_host) {
  host_toolchain = "//build/toolchain/termux:$host_cpu"
}'''
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(buildconfig_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Modified {buildconfig_path}")

def modify_sysroot_gni(engine_src_path):
    """Modify sysroot.gni to support termux."""
    sysroot_path = engine_src_path / "build" / "config" / "sysroot.gni"
    
    with open(sysroot_path, 'r') as f:
        content = f.read()
    
    # Add termux sysroot support
    pattern = r'(if \(current_toolchain == default_toolchain && target_sysroot != ""\) \{\s*sysroot = target_sysroot)'
    replacement = '''if (current_toolchain == default_toolchain && target_sysroot != "") {
  sysroot = target_sysroot
} else if (is_termux && custom_sysroot != "") {
  sysroot = custom_sysroot'''
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(sysroot_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Modified {sysroot_path}")

def modify_testing_build_gn(engine_src_path):
    """Modify flutter/shell/testing/BUILD.gn for termux support."""
    testing_path = engine_src_path / "flutter" / "shell" / "testing" / "BUILD.gn"
    
    if not testing_path.exists():
        print(f"⚠️  Warning: {testing_path} not found, skipping")
        return
    
    with open(testing_path, 'r') as f:
        content = f.read()
    
    # Add termux-specific swiftshader handling
    pattern = r'(if \(impeller_supports_rendering\) \{\s*deps \+= \[\s*":tester_gpu_configuration",\s*"//flutter/impeller",\s*"//flutter/third_party/swiftshader/src/Vulkan:swiftshader_libvulkan_static",\s*\]\s*})'
    replacement = '''if (impeller_supports_rendering) {
    deps += [
      ":tester_gpu_configuration",
      "//flutter/impeller",
      "//flutter/third_party/swiftshader/src/Vulkan:swiftshader_libvulkan_static",
    ]
    if (is_termux) {
      libs += [ "vk_swiftshader" ]
      deps -= [ "//flutter/third_party/swiftshader/src/Vulkan:swiftshader_libvulkan_static" ]
    }
  }'''
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(testing_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Modified {testing_path}")

def modify_skia_features(engine_src_path):
    """Modify Skia SkFeatures.h to prevent Android detection in Termux."""
    skia_features_path = engine_src_path / "flutter" / "third_party" / "skia" / "include" / "private" / "base" / "SkFeatures.h"
    
    if not skia_features_path.exists():
        print(f"⚠️  Warning: {skia_features_path} not found, skipping")
        return
    
    with open(skia_features_path, 'r') as f:
        content = f.read()
    
    # Prevent Skia from detecting Android in Termux environment
    pattern = r'#elif defined\(ANDROID\) \|\| defined\(__ANDROID__\)'
    replacement = '#elif (defined(ANDROID) || defined(__ANDROID__)) && !defined(__TERMUX__)'
    content = content.replace(pattern, replacement)
    
    with open(skia_features_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Modified {skia_features_path}")

def setup_termux_support(flutter_root):
    """Set up complete Termux support for Flutter engine."""
    flutter_path = Path(flutter_root)
    engine_src_path = flutter_path / "engine" / "src"
    
    if not engine_src_path.exists():
        raise ValueError(f"Flutter engine source not found at {engine_src_path}")
    
    print("Setting up Termux support for Flutter engine...")
    print(f"Engine source path: {engine_src_path}")
    
    # Create termux configuration files
    create_termux_build_gn(engine_src_path)
    create_termux_gni(engine_src_path)
    create_termux_toolchain(engine_src_path)
    
    # Modify existing files
    modify_buildconfig_gn(engine_src_path)
    modify_sysroot_gni(engine_src_path)
    modify_testing_build_gn(engine_src_path)
    modify_skia_features(engine_src_path)
    
    print("✅ Termux support setup completed!")
    print("✅ Android log library support included (libs = ['log'])")
    print("✅ Skia Android detection prevented for Termux")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python setup_termux_support.py <flutter_root_path>")
        sys.exit(1)
    
    flutter_root = sys.argv[1]
    setup_termux_support(flutter_root)